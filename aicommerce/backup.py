"""Backup and restore of the whole `data/` directory (brain.db, events.db,
scheduler.db). Master-plan Milestone 7 requirement: "backup automático de
base de datos y restauración probada" — this makes that a real, tested
operation rather than a promise.

Backups are plain file copies under `data/backups/<timestamp>/`, so restoring
is just copying back — no special tooling needed to inspect a backup by hand.
"""
from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

DB_FILENAMES = ("brain.db", "events.db", "scheduler.db")


def backup_data_dir(data_dir: Path, backups_root: Path | None = None) -> Path:
    """Copy every known DB file in `data_dir` into a new timestamped folder
    under `backups_root` (default: `data_dir/backups`). Returns that folder.
    Missing files (e.g. events.db before the first event) are skipped, not
    an error — a fresh install has less to back up, not a broken one.
    """
    backups_root = backups_root or (data_dir / "backups")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    dest = backups_root / stamp
    dest.mkdir(parents=True, exist_ok=False)

    copied = []
    for name in DB_FILENAMES:
        src = data_dir / name
        if src.exists():
            shutil.copy2(src, dest / name)
            copied.append(name)

    if not copied:
        dest.rmdir()
        raise FileNotFoundError(f"nothing to back up in {data_dir} — no known DB files present")

    return dest


def restore_data_dir(backup_dir: Path, data_dir: Path) -> list[str]:
    """Copy every DB file found in `backup_dir` back into `data_dir`,
    overwriting what's there. Returns the list of filenames restored.

    Callers should treat this as destructive to `data_dir`'s current DB
    files — the caller (CLI/API) is responsible for confirming with a human
    before invoking this against a live system's data directory.
    """
    if not backup_dir.is_dir():
        raise FileNotFoundError(f"backup directory not found: {backup_dir}")

    restored = []
    for name in DB_FILENAMES:
        src = backup_dir / name
        if src.exists():
            data_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, data_dir / name)
            restored.append(name)

    if not restored:
        raise FileNotFoundError(f"no known DB files found in backup: {backup_dir}")

    return restored


def list_backups(data_dir: Path, backups_root: Path | None = None) -> list[Path]:
    backups_root = backups_root or (data_dir / "backups")
    if not backups_root.is_dir():
        return []
    return sorted(p for p in backups_root.iterdir() if p.is_dir())
