import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Tuple


def get_connection(db_path: str) -> sqlite3.Connection:
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_file)


def initialize_database(db_path: str) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT NOT NULL,
                port INTEGER NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )
        connection.commit()


def insert_scan_results(
    db_path: str,
    target: str,
    results: Iterable[Tuple[int, str] | Tuple[int, str, str] | Tuple[int, str, str, str]],
    timestamp: str | None = None,
) -> int:
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    rows = []
    for entry in results:
        if len(entry) == 2:
            port, status = entry
        elif len(entry) == 3:
            port, _, status = entry
        elif len(entry) == 4:
            port, _, _, status = entry
        else:
            raise ValueError("Each scan result must be (port, status), (port, service, status), or (port, service, version, status).")
        rows.append((target, port, status, timestamp))

    with get_connection(db_path) as connection:
        connection.executemany(
            "INSERT INTO scans(target, port, status, timestamp) VALUES (?, ?, ?, ?)",
            rows,
        )
        connection.commit()

    return len(rows)
