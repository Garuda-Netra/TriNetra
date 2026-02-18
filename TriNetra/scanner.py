from __future__ import annotations

import errno
import os
import random
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Iterable, List, Tuple

try:
    from scapy.all import IP, TCP, sr1
    _SCAPY_AVAILABLE = True
except Exception:
    IP = TCP = sr1 = None
    _SCAPY_AVAILABLE = False


def parse_port_range(port_range: str) -> List[int]:
    """Parse a port range string such as '1-1024' or '22,80,443'."""
    port_set = set()

    for chunk in port_range.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue

        if "-" in chunk:
            start_str, end_str = chunk.split("-", maxsplit=1)
            start = int(start_str)
            end = int(end_str)
            if start > end:
                raise ValueError(f"Invalid range '{chunk}': start cannot be greater than end.")
            port_set.update(range(start, end + 1))
        else:
            port_set.add(int(chunk))

    if not port_set:
        raise ValueError("No ports were provided.")

    ports = sorted(port_set)
    if ports[0] < 1 or ports[-1] > 65535:
        raise ValueError("Ports must be in the range 1-65535.")

    return ports


def is_root() -> bool:
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def get_scan_mode_message() -> str:
    if is_root() and _SCAPY_AVAILABLE:
        return "[INFO] Running privileged SYN scan (root detected)"
    if is_root() and not _SCAPY_AVAILABLE:
        return "[INFO] Running TCP connect scan (scapy unavailable)"
    return "[INFO] Running TCP connect scan (non-root mode)"


def resolve_target(target: str) -> str:
    """Resolve a target domain or IP to an IPv4 address."""
    return socket.gethostbyname(target)


def _state_priority(status: str) -> int:
    priorities = {
        "OPEN": 4,
        "CLOSED": 3,
        "FILTERED": 2,
        "ERROR": 1,
    }
    return priorities.get(status, 0)


def _is_valid_port(port: int) -> bool:
    return 1 <= port <= 65535


def _normalize_timeout(timeout: float) -> float:
    try:
        timeout_value = float(timeout)
    except (TypeError, ValueError):
        return 0.8
    return timeout_value if timeout_value > 0 else 0.8


def _build_errno_set(*names: str) -> set[int]:
    """Collect errno constants that exist on this platform into a set."""
    codes: set[int] = set()
    for name in names:
        val = getattr(errno, name, None)
        if val is not None:
            codes.add(val)
    return codes


# Definitive "port is closed" — the host actively refused the connection.
_CLOSED_ERRNOS: set[int] = _build_errno_set("ECONNREFUSED")

# Anything that means "no response / blocked / unreachable" → FILTERED.
_FILTERED_ERRNOS: set[int] = _build_errno_set(
    # Timeout / unreachable / down
    "ETIMEDOUT",
    "EHOSTUNREACH",
    "ENETUNREACH",
    "EHOSTDOWN",
    "ENETDOWN",
    # Firewall / permission denied
    "EACCES",
    "EPERM",
    # Non-blocking / in-progress (socket timed out before completing)
    "EINPROGRESS",
    "EALREADY",
    "EWOULDBLOCK",
    "EAGAIN",
    # Windows-specific Winsock codes (10060 = WSAETIMEDOUT, etc.)
    "WSAETIMEDOUT",
    "WSAEHOSTUNREACH",
    "WSAENETUNREACH",
    "WSAEHOSTDOWN",
    "WSAENETDOWN",
    "WSAECONNREFUSED",   # handled separately below, but kept as safety net
    "WSAEINPROGRESS",
    "WSAEALREADY",
    "WSAEWOULDBLOCK",
    "WSAEAGAIN",
    "WSAEACCES",
    "WSAEPERM",
)

# On Windows, WSAECONNREFUSED (10061) should also map to CLOSED.
_CLOSED_ERRNOS |= _build_errno_set("WSAECONNREFUSED")
# …and remove it from FILTERED if it landed there.
_FILTERED_ERRNOS -= _CLOSED_ERRNOS


def _classify_errno(error_number: int | None) -> str:
    """Map a connect_ex / OSError errno to a port state string."""
    if error_number is None or error_number == 0:
        return "ERROR"

    if error_number in _CLOSED_ERRNOS:
        return "CLOSED"

    if error_number in _FILTERED_ERRNOS:
        return "FILTERED"

    # Fallback: treat any other non-zero code as FILTERED rather than ERROR,
    # because connect_ex returning *any* OS-level failure means the probe
    # did not succeed — the port is either filtered or unreachable, not
    # in an "internal error" state.  This matches Nmap's TCP-connect
    # behavior where only RST → closed, everything else → filtered.
    return "FILTERED"


def _standard_service_name(port: int) -> str:
    try:
        return socket.getservbyport(port, "tcp").upper()
    except OSError:
        return "Unknown"


def _detect_banner_service(ip_address: str, port: int, timeout: float) -> str:
    try:
        with socket.create_connection((ip_address, port), timeout=timeout) as sock:
            sock.settimeout(timeout)

            if port in {80, 8080, 8000, 8888}:
                try:
                    sock.sendall(b"HEAD / HTTP/1.0\r\nHost: target\r\n\r\n")
                except OSError:
                    pass

            try:
                banner = sock.recv(1024)
            except OSError:
                return "Unknown"

            if not banner:
                return "Unknown"

            banner_text = banner.decode("utf-8", errors="ignore").strip().lower()

            if "ssh-" in banner_text:
                return "SSH"
            if "ftp" in banner_text:
                return "FTP"
            if "smtp" in banner_text:
                return "SMTP"
            if "mysql" in banner_text:
                return "MySQL"
            if "postgres" in banner_text or "postgresql" in banner_text:
                return "PostgreSQL"
            if "redis" in banner_text:
                return "Redis"
            if "mongo" in banner_text or "mongodb" in banner_text:
                return "MongoDB"
            if "http/" in banner_text or "server:" in banner_text or "content-type:" in banner_text:
                if "https" in banner_text:
                    return "HTTPS"
                return "HTTP"
    except OSError:
        return "Unknown"

    return "Unknown"


def detect_service(ip_address: str, port: int, timeout: float = 1.0) -> str:
    """Detect service using stdlib mapping and banner grabbing.

    Priority order (matches Nmap basic behaviour):
      1. socket.getservbyport() — authoritative for standard ports.
      2. Banner grabbing — used ONLY when getservbyport returns Unknown.
    This ensures common ports (80→HTTP, 443→HTTPS, 22→SSH …) are never
    overridden by ambiguous banner text.
    """
    if not _is_valid_port(port):
        raise ValueError(f"Invalid port {port}. Port must be in the range 1-65535.")

    effective_timeout = _normalize_timeout(timeout)

    # --- First priority: OS / IANA service database ---
    standard = _standard_service_name(port)
    if standard != "Unknown":
        return standard

    # --- Second priority: banner grabbing for non-standard ports ---
    banner_service = _detect_banner_service(ip_address, port, effective_timeout)
    if banner_service != "Unknown":
        return banner_service

    return "Unknown"


def _probe_once(ip_address: str, port: int, timeout: float) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result_code = sock.connect_ex((ip_address, port))

            if result_code == 0:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                return "OPEN"

            return _classify_errno(result_code)
    except socket.timeout:
        return "FILTERED"
    except ConnectionRefusedError:
        return "CLOSED"
    except OSError as error:
        return _classify_errno(getattr(error, "errno", None))
    except Exception:
        return "ERROR"


def syn_scan_port(ip_address: str, port: int, timeout: float = 0.8) -> str:
    if not _is_valid_port(port):
        raise ValueError(f"Invalid port {port}. Port must be in the range 1-65535.")

    effective_timeout = _normalize_timeout(timeout)

    if not (is_root() and _SCAPY_AVAILABLE):
        return check_port(ip_address, port, effective_timeout, retry_count=1)

    try:
        packet = IP(dst=ip_address) / TCP(dport=port, flags="S")
        response = sr1(packet, timeout=effective_timeout, verbose=0)

        if response is None:
            return "FILTERED"

        if response.haslayer(TCP):
            tcp_layer = response.getlayer(TCP)
            flags = int(tcp_layer.flags)
            if flags & 0x12 == 0x12:
                return "OPEN"
            if flags & 0x04:
                return "CLOSED"

        return "FILTERED"
    except PermissionError:
        return "ERROR"
    except OSError:
        return "ERROR"
    except Exception:
        return "ERROR"


def scan_port(ip_address: str, port: int, timeout: float = 0.8, retry_count: int = 1) -> str:
    if is_root() and _SCAPY_AVAILABLE:
        return syn_scan_port(ip_address, port, timeout)
    return check_port(ip_address, port, timeout, retry_count)


def check_port(ip_address: str, port: int, timeout: float = 0.8, retry_count: int = 1) -> str:
    """Check a single TCP port and return OPEN/CLOSED/FILTERED/ERROR.

    Signature remains compatible with existing calls using
    check_port(ip_address, port, timeout).
    """
    if not _is_valid_port(port):
        raise ValueError(f"Invalid port {port}. Port must be in the range 1-65535.")

    effective_timeout = _normalize_timeout(timeout)
    attempts = max(1, int(retry_count) + 1)
    best_status = "ERROR"

    for attempt_index in range(attempts):
        status = _probe_once(ip_address, port, effective_timeout)

        if status == "OPEN":
            return "OPEN"

        if _state_priority(status) > _state_priority(best_status):
            best_status = status

        if attempt_index < attempts - 1:
            time.sleep(random.uniform(0.01, 0.05))

    return best_status


def detect_service_version(ip_address: str, port: int, timeout: float = 1.0) -> str:
    if not _is_valid_port(port):
        raise ValueError(f"Invalid port {port}. Port must be in the range 1-65535.")

    effective_timeout = _normalize_timeout(timeout)

    try:
        with socket.create_connection((ip_address, port), timeout=effective_timeout) as sock:
            sock.settimeout(effective_timeout)

            if port in {80, 8080, 8000, 8888, 443}:
                try:
                    sock.sendall(b"HEAD / HTTP/1.0\r\nHost: target\r\n\r\n")
                except OSError:
                    pass

            try:
                banner = sock.recv(1024)
            except OSError:
                return ""

            if not banner:
                return ""

            text = banner.decode("utf-8", errors="ignore")

            server_line = next(
                (
                    line.split(":", 1)[1].strip()
                    for line in text.splitlines()
                    if line.lower().startswith("server:")
                ),
                "",
            )
            if server_line:
                return server_line[:80]

            match = re.search(
                r"(OpenSSH[_\-/ ]?[0-9A-Za-z.]+|nginx[/ ]?[0-9.]+|Apache[/ ]?[0-9.]+|cloudflare|Postfix[/ ]?[0-9A-Za-z.]+|Exim[/ ]?[0-9A-Za-z.]+|Microsoft-IIS/[0-9.]+)",
                text,
                flags=re.IGNORECASE,
            )
            if match:
                return match.group(1).replace("_", " ")[:80]

            first_line = text.strip().splitlines()[0].strip() if text.strip() else ""
            return first_line[:80]
    except OSError:
        return ""


def scan_ports(
    ip_address: str,
    ports: Iterable[int],
    timeout: float = 0.8,
    max_threads: int = 100,
    retry_count: int = 1,
) -> List[Tuple[int, str, str]]:
    """Scan ports concurrently and return a list of (port, service, status).

    The return order matches the input order.
    """
    port_list = list(ports)
    if not port_list:
        return []

    invalid_ports = [port for port in port_list if not _is_valid_port(port)]
    if invalid_ports:
        invalid_preview = ", ".join(str(port) for port in invalid_ports[:10])
        suffix = "..." if len(invalid_ports) > 10 else ""
        raise ValueError(f"Invalid ports found: {invalid_preview}{suffix}. Valid range is 1-65535.")

    effective_timeout = _normalize_timeout(timeout)
    safe_max_threads = max(1, min(int(max_threads), 200))
    worker_count = max(1, min(safe_max_threads, len(port_list)))
    results_by_index: Dict[int, Tuple[int, str, str]] = {}

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_to_index = {
            executor.submit(scan_port, ip_address, port, effective_timeout, retry_count): index
            for index, port in enumerate(port_list)
        }

        for future in as_completed(future_to_index):
            index = future_to_index[future]
            port = port_list[index]
            try:
                status = future.result()
            except Exception:
                status = "ERROR"

            service = "Unknown"
            if status == "OPEN":
                service = detect_service(ip_address, port, effective_timeout)

            results_by_index[index] = (port, service, status)

    return [results_by_index[index] for index in range(len(port_list))]
