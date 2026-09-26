"""SQLite-backed Company Brain.

Model-agnostic, persistent, queryable organizational memory. Any process
(any model provider) can read/write this store — the model can be replaced
without losing institutional memory, per the master context.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Optional

from .models import MemoryKind, MemoryRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS memory (
    id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    content TEXT NOT NULL,
    source TEXT NOT NULL,
    confidence TEXT NOT NULL,
    tags TEXT NOT NULL,
    metadata TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    superseded_by TEXT
);
CREATE INDEX IF NOT EXISTS idx_memory_kind ON memory(kind);
CREATE INDEX IF NOT EXISTS idx_memory_timestamp ON memory(timestamp);
"""


class CompanyBrain:
    """Persistent organizational memory, independent of any model provider."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "CompanyBrain":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------
    def record(self, memory: MemoryRecord) -> MemoryRecord:
        self._conn.execute(
            "INSERT INTO memory VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            memory.to_row(),
        )
        self._conn.commit()
        return memory

    def supersede(self, old_id: str, new: MemoryRecord) -> MemoryRecord:
        """Record a new memory and mark the old one as superseded by it.

        Used when a memory turns out to be stale/wrong — the old record is kept
        for auditability but flagged, rather than silently overwritten.
        """
        self.record(new)
        self._conn.execute(
            "UPDATE memory SET superseded_by = ? WHERE id = ?", (new.id, old_id)
        )
        self._conn.commit()
        return new

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def get(self, memory_id: str) -> Optional[MemoryRecord]:
        row = self._conn.execute(
            "SELECT id, kind, content, source, confidence, tags, metadata, timestamp, superseded_by "
            "FROM memory WHERE id = ?",
            (memory_id,),
        ).fetchone()
        return MemoryRecord.from_row(row) if row else None

    def query(
        self,
        kind: Optional[MemoryKind] = None,
        tags: Optional[Iterable[str]] = None,
        include_superseded: bool = False,
        limit: int = 100,
    ) -> list[MemoryRecord]:
        sql = (
            "SELECT id, kind, content, source, confidence, tags, metadata, timestamp, superseded_by "
            "FROM memory WHERE 1=1"
        )
        params: list = []
        if kind is not None:
            sql += " AND kind = ?"
            params.append(kind.value)
        if not include_superseded:
            sql += " AND superseded_by IS NULL"
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = self._conn.execute(sql, params).fetchall()
        records = [MemoryRecord.from_row(r) for r in rows]

        if tags:
            wanted = set(tags)
            records = [r for r in records if wanted & set(r.tags)]

        return records

    def all(self, include_superseded: bool = False) -> list[MemoryRecord]:
        return self.query(include_superseded=include_superseded, limit=10_000)
