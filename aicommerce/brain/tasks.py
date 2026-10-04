"""Real task/objective tracking — Jean's explicit, repeated ask: the team must
actually complete tasks and objectives with a checkable status, not just
narrative text in memory that happens to say "done". A MemoryRecord tagged
"done" is a claim; a Task here is a row with a real status that can only move
through `update_status`, so "what's actually done vs pending" is a query, not
an opinion.

This is deliberately separate from CompanyBrain's freeform memory: memory is
for reasoning/context ("what do I know"), this is for execution state ("what
is actually in progress, blocked, or finished, and who owns it").
"""
from __future__ import annotations

import sqlite3
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


_TERMINAL = {TaskStatus.DONE, TaskStatus.CANCELLED}


@dataclass
class Task:
    objective: str  # groups related tasks under one goal, e.g. "validate product X"
    title: str
    owner: str  # agent name, e.g. "research", "marketing" -- who is actually on it
    status: TaskStatus = TaskStatus.PENDING
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_row(self) -> tuple:
        return (
            self.id, self.objective, self.title, self.owner, self.status.value,
            self.notes, self.created_at.isoformat(), self.updated_at.isoformat(),
        )

    @staticmethod
    def from_row(row: tuple) -> "Task":
        id_, objective, title, owner, status, notes, created_at, updated_at = row
        return Task(
            id=id_, objective=objective, title=title, owner=owner,
            status=TaskStatus(status), notes=notes,
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(updated_at),
        )


class InvalidTaskTransition(ValueError):
    pass


_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    objective TEXT NOT NULL,
    title TEXT NOT NULL,
    owner TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_objective ON tasks(objective);
CREATE INDEX IF NOT EXISTS idx_tasks_owner ON tasks(owner);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
"""


class TaskBoard:
    """Persistent, queryable task state. Same thread-safety pattern as
    CompanyBrain (a web server may call this from any threadpool thread)."""

    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self.db_path = str(db_path)
        if self.db_path != ":memory:":
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock:
            self._conn.executescript(_SCHEMA)
            self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def create(self, objective: str, title: str, owner: str) -> Task:
        task = Task(objective=objective, title=title, owner=owner)
        with self._lock:
            self._conn.execute("INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?)", task.to_row())
            self._conn.commit()
        return task

    def get(self, task_id: str) -> Optional[Task]:
        with self._lock:
            row = self._conn.execute(
                "SELECT id, objective, title, owner, status, notes, created_at, updated_at "
                "FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        return Task.from_row(row) if row else None

    def update_status(self, task_id: str, status: TaskStatus, notes: str = "") -> Task:
        task = self.get(task_id)
        if task is None:
            raise KeyError(f"no task with id {task_id}")
        if task.status in _TERMINAL and status != task.status:
            raise InvalidTaskTransition(
                f"task {task_id} is already '{task.status.value}' (terminal) -- "
                f"cannot move it to '{status.value}'"
            )
        task.status = status
        if notes:
            task.notes = notes
        task.updated_at = datetime.now(timezone.utc)
        with self._lock:
            self._conn.execute(
                "UPDATE tasks SET status = ?, notes = ?, updated_at = ? WHERE id = ?",
                (task.status.value, task.notes, task.updated_at.isoformat(), task.id),
            )
            self._conn.commit()
        return task

    def list(
        self,
        objective: Optional[str] = None,
        owner: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        limit: int = 200,
    ) -> list[Task]:
        sql = (
            "SELECT id, objective, title, owner, status, notes, created_at, updated_at "
            "FROM tasks WHERE 1=1"
        )
        params: list = []
        if objective is not None:
            sql += " AND objective = ?"
            params.append(objective)
        if owner is not None:
            sql += " AND owner = ?"
            params.append(owner)
        if status is not None:
            sql += " AND status = ?"
            params.append(status.value)
        sql += " ORDER BY created_at ASC LIMIT ?"
        params.append(limit)
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
        return [Task.from_row(r) for r in rows]

    def summary(self) -> dict:
        """Real counts by status -- 'done' here means rows actually marked
        done, not a claim made in a chat message."""
        tasks = self.list(limit=10_000)
        by_status: dict[str, int] = {s.value: 0 for s in TaskStatus}
        for t in tasks:
            by_status[t.status.value] += 1
        return {"total": len(tasks), "by_status": by_status}
