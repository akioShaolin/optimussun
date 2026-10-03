import hashlib
import sqlite3
from pathlib import Path


TABLES = (
    "manufacturer", "inverter", "mppt", "module", "inverter_system",
    "inverter_communication", "inverter_output_mode",
)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def create_snapshot(source_path, snapshot_path):
    source = Path(source_path).resolve()
    target = Path(snapshot_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        raise FileExistsError(f"Snapshot já existe: {target}")
    original_before = sha256_file(source)
    with sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True) as src:
        with sqlite3.connect(target) as dst:
            src.backup(dst)
    original_after = sha256_file(source)
    if original_before != original_after:
        raise RuntimeError("O SQLite de origem mudou durante a criação do snapshot.")
    return {
        "source_id": "optimus-sun-sqlite-catalog",
        "source_path": str(source),
        "source_sha256": original_before,
        "snapshot_path": str(target),
        "snapshot_sha256": sha256_file(target),
    }


def read_snapshot(snapshot_path):
    path = Path(snapshot_path).resolve()
    with sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True) as connection:
        connection.row_factory = sqlite3.Row
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        fk_issues = [dict(row) for row in connection.execute("PRAGMA foreign_key_check")]
        rows = {
            table: [dict(row) for row in connection.execute(f"SELECT * FROM {table} ORDER BY ID")]
            for table in TABLES
        }
    return {"integrity": integrity, "foreign_key_issues": fk_issues, "tables": rows}

