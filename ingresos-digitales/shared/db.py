"""SQLite helper: data/app.db. Holds the LLM usage log for cost tracking."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from shared.config import DATA_DIR

SCHEMA = """
CREATE TABLE IF NOT EXISTS llm_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL DEFAULT (datetime('now')),
    model TEXT NOT NULL,
    purpose TEXT,
    input_tokens INTEGER NOT NULL,
    output_tokens INTEGER NOT NULL,
    cost_usd REAL NOT NULL
);
"""


def connect(path: Path | None = None) -> sqlite3.Connection:
    path = path or DATA_DIR / "app.db"
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    return conn
