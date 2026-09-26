"""Data model for the Company Brain — persistent organizational memory.

Memory classes per the master context:
  episodic     — what happened
  semantic     — what the company knows
  procedural   — how to do something
  decision     — why a decision was made
  experiment   — what was tested and learned
  institutional — stable rules/knowledge
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class MemoryKind(str, Enum):
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    DECISION = "decision"
    EXPERIMENT = "experiment"
    INSTITUTIONAL = "institutional"


class Confidence(str, Enum):
    FACT = "fact"
    INFERENCE = "inference"
    HYPOTHESIS = "hypothesis"
    UNKNOWN = "unknown"


@dataclass
class MemoryRecord:
    """A single unit of organizational memory.

    `source` and `timestamp` are required so freshness/provenance can always be
    established later, per the Reality-First / Evidence-First principle.
    """

    kind: MemoryKind
    content: str
    source: str
    confidence: Confidence = Confidence.UNKNOWN
    tags: tuple[str, ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    superseded_by: Optional[str] = None

    def to_row(self) -> tuple:
        import json

        return (
            self.id,
            self.kind.value,
            self.content,
            self.source,
            self.confidence.value,
            json.dumps(list(self.tags)),
            json.dumps(self.metadata),
            self.timestamp.isoformat(),
            self.superseded_by,
        )

    @staticmethod
    def from_row(row: tuple) -> "MemoryRecord":
        import json

        (id_, kind, content, source, confidence, tags, metadata, ts, superseded_by) = row
        return MemoryRecord(
            id=id_,
            kind=MemoryKind(kind),
            content=content,
            source=source,
            confidence=Confidence(confidence),
            tags=tuple(json.loads(tags)),
            metadata=json.loads(metadata),
            timestamp=datetime.fromisoformat(ts),
            superseded_by=superseded_by,
        )
