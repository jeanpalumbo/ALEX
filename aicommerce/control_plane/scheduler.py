"""Scheduler — recurring jobs (daily business review, SEO crawl, etc.).

Polling-based: something must call `run_due()` periodically — the CEO Console
does this from a background thread (see `aicommerce/webapp/server.py`), so it
now runs automatically whenever the server is up, closing the earlier PARTIAL
gap. Optionally persisted to SQLite (pass `db_path`): each job's `last_run` is
loaded on `add_job` and saved on every run, so a process restart does not
forget when a job last fired and re-trigger it immediately — this is what
prevents a paid autonomous CEO tick (or any job) from double-firing right
after a restart.
"""
from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional

_SCHEMA = """
CREATE TABLE IF NOT EXISTS scheduler_jobs (
    name TEXT PRIMARY KEY,
    last_run TEXT
);
"""


@dataclass
class Job:
    name: str
    interval: timedelta
    func: Callable[[], None]
    last_run: Optional[datetime] = None

    def due(self, now: datetime) -> bool:
        return self.last_run is None or (now - self.last_run) >= self.interval


class Scheduler:
    def __init__(
        self,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
        db_path: Optional[str | Path] = None,
    ) -> None:
        self._clock = clock
        self._jobs: dict[str, Job] = {}
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()
        if db_path is not None:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
            with self._lock:
                self._conn.executescript(_SCHEMA)
                self._conn.commit()

    def _load_last_run(self, name: str) -> Optional[datetime]:
        if self._conn is None:
            return None
        with self._lock:
            row = self._conn.execute(
                "SELECT last_run FROM scheduler_jobs WHERE name = ?", (name,)
            ).fetchone()
        return datetime.fromisoformat(row[0]) if row and row[0] else None

    def _save_last_run(self, name: str, when: datetime) -> None:
        if self._conn is None:
            return
        with self._lock:
            self._conn.execute(
                "INSERT INTO scheduler_jobs (name, last_run) VALUES (?, ?) "
                "ON CONFLICT(name) DO UPDATE SET last_run = excluded.last_run",
                (name, when.isoformat()),
            )
            self._conn.commit()

    def add_job(self, name: str, interval: timedelta, func: Callable[[], None]) -> None:
        if name in self._jobs:
            raise ValueError(f"job '{name}' already scheduled")
        job = Job(name=name, interval=interval, func=func, last_run=self._load_last_run(name))
        self._jobs[name] = job

    def remove_job(self, name: str) -> None:
        self._jobs.pop(name, None)

    def run_due(self, on_error: Optional[Callable[[str, Exception], None]] = None) -> list[str]:
        """Run every job whose interval has elapsed. Returns names of jobs run.

        One job's exception never stops the others in the same call. A job
        that raises does NOT get `last_run` advanced, so it is retried on the
        next call instead of being silently skipped for a full interval.
        `on_error(job_name, exc)`, if given, is called for a failed job —
        use it to record the failure somewhere visible (e.g. Company Brain);
        without it, failures are only observable via the return value missing
        that job's name.
        """
        now = self._clock()
        ran = []
        for job in self._jobs.values():
            if not job.due(now):
                continue
            try:
                job.func()
            except Exception as exc:  # noqa: BLE001 — one job's bug must not break the others
                if on_error is not None:
                    on_error(job.name, exc)
                continue
            job.last_run = now
            self._save_last_run(job.name, now)
            ran.append(job.name)
        return ran

    def jobs(self) -> list[Job]:
        return list(self._jobs.values())

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
