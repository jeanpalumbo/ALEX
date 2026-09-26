"""Event Bus — pub/sub so agents react to events instead of polling.

Optionally persisted to SQLite (pass `db_path`) so the audit/event stream
survives a restart, per the master plan's Milestone 7 requirement. Without a
`db_path` it behaves exactly as before (in-memory only) — existing callers
and tests are unaffected.
"""
from __future__ import annotations

import json
import sqlite3
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    seq INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    payload TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(type);
"""


@dataclass
class Event:
    type: str
    payload: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus:
    def __init__(self, db_path: Optional[str | Path] = None) -> None:
        self._subscribers: dict[str, list[Callable[[Event], None]]] = defaultdict(list)
        self._log: list[Event] = []
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()
        if db_path is not None:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
            with self._lock:
                self._conn.executescript(_SCHEMA)
                self._conn.commit()
            self._load_recent_into_memory()

    def _load_recent_into_memory(self, limit: int = 500) -> None:
        with self._lock:
            rows = self._conn.execute(
                "SELECT type, payload, timestamp FROM events ORDER BY seq DESC LIMIT ?", (limit,)
            ).fetchall()
        for type_, payload, ts in reversed(rows):
            self._log.append(Event(type=type_, payload=json.loads(payload), timestamp=datetime.fromisoformat(ts)))

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._subscribers[event_type].append(handler)

    def publish(self, event_type: str, payload: dict | None = None) -> Event:
        event = Event(type=event_type, payload=payload or {})
        self._log.append(event)
        if self._conn is not None:
            with self._lock:
                self._conn.execute(
                    "INSERT INTO events (type, payload, timestamp) VALUES (?, ?, ?)",
                    (event.type, json.dumps(event.payload), event.timestamp.isoformat()),
                )
                self._conn.commit()
        for handler in self._subscribers.get(event_type, []):
            handler(event)
        return event

    def history(self, event_type: str | None = None, limit: Optional[int] = None, offset: int = 0) -> list[Event]:
        """In-memory view (fast, capped at the last ~500 persisted events plus
        anything published since startup). Use `query_persisted` for a full,
        paginated read straight from disk."""
        events = self._log if event_type is None else [e for e in self._log if e.type == event_type]
        if offset:
            events = events[:-offset] if offset < len(events) else []
        if limit is not None:
            events = events[-limit:]
        return events

    def query_persisted(self, event_type: str | None = None, limit: int = 50, offset: int = 0) -> list[Event]:
        """Paginated read directly from the durable store. Requires `db_path`."""
        if self._conn is None:
            return self.history(event_type, limit=limit, offset=offset)
        sql = "SELECT type, payload, timestamp FROM events"
        params: list = []
        if event_type is not None:
            sql += " WHERE type = ?"
            params.append(event_type)
        sql += " ORDER BY seq DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
        return [Event(type=t, payload=json.loads(p), timestamp=datetime.fromisoformat(ts)) for t, p, ts in rows]
