import argparse
import textwrap
from pathlib import Path
from typing import List, Tuple

from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TaskProgressColumn

from .database import initialize_database, insert_scan_results
from .scanner import (
    detect_service,
    detect_service_version,
    get_scan_mode_message,
    parse_port_range,
    resolve_target,
    scan_port,
)
from .ui import (
    console,
    print_banner,
    print_error,
    print_results_header,
    print_result_row,
    print_scan_mode,
    print_scan_target,
    print_summary,
)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trinetra",
        description=textwrap.dedent("""\
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
             त्रिनेत्र  TRINETRA — Third Eye Scanner
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

            A Python CLI port scanner with Rich output,
            progress tracking, and SQLite result storage.

            ॐ त्र्यम्बकं यजामहे सुगन्धिं पुष्टिवर्धनम् ।
            उर्वारुकमिव बन्धनान्मृत्योर्मुक्षीय मामृतात् ॥
        """),
        epilog=textwrap.dedent("""\
            ━━━━━ Examples ━━━━━━━━━━━━━━━━━━━━━━━━━━━

              %(prog)s 127.0.0.1 20-80
              %(prog)s scanme.nmap.org 22,80,443 --timeout 0.3
              %(prog)s 192.168.1.1 1-1024 --db data/custom.db

            ━━━━━ Flags ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

              --timeout   Socket timeout in seconds (default 0.5)
              --db        Path to SQLite database file
              -h, --help  Show this help message

            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            Created by Garuda Netra
            ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        help="Target IP address or domain name (e.g. 127.0.0.1, scanme.nmap.org)",
    )
    parser.add_argument(
        "ports",
        help="Port specification: range '1-1024' or comma-separated '22,80,443'",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.5,
        help="Socket timeout in seconds (default: 0.5)",
    )
    parser.add_argument(
        "--db",
        default=str(Path("data") / "trinetra_scans.db"),
        help="SQLite database path (default: data/trinetra_scans.db)",
    )
    return parser


def perform_scan(ip_address: str, ports: List[int], timeout: float) -> List[Tuple[int, str, str, str]]:
    results: List[Tuple[int, str, str, str]] = []

    progress = Progress(
        SpinnerColumn(spinner_name="dots", style="bright_yellow"),
        TextColumn("[bold bright_blue]{task.description}"),
        BarColumn(bar_width=40, style="dim", complete_style="bright_yellow", finished_style="green"),
        TaskProgressColumn(),
        TextColumn("[dim]•[/dim]"),
        TimeElapsedColumn(),
        transient=True,
        console=console,
    )

    with progress:
        task_id = progress.add_task("Scanning ports", total=len(ports))
        print_results_header()
        for port in ports:
            status = scan_port(ip_address, port, timeout=timeout)
            service = "Unknown"
            version = ""
            if status == "OPEN":
                service = detect_service(ip_address, port, timeout=timeout)
                version = detect_service_version(ip_address, port, timeout=timeout)
            results.append((port, service, version, status))
            print_result_row(port, service, version, status)
            progress.advance(task_id)

    return results


def run() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    print_banner()

    try:
        ports = parse_port_range(args.ports)
        ip_address = resolve_target(args.target)
        initialize_database(args.db)
    except ValueError as error:
        print_error(str(error))
        return 2
    except OSError as error:
        print_error(f"Network or database initialization failed: {error}")
        return 1

    print_scan_target(args.target, ip_address, len(ports))
    print_scan_mode(get_scan_mode_message())

    try:
        results = perform_scan(ip_address, ports, timeout=args.timeout)
        saved_rows = insert_scan_results(args.db, args.target, results)
    except OSError as error:
        print_error(f"Scan failed: {error}")
        return 1

    open_count = sum(1 for _, _, _, status in results if status == "OPEN")
    closed_count = len(results) - open_count
    print_summary(args.target, ip_address, open_count, closed_count, saved_rows, args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
