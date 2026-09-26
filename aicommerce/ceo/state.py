"""Observable CEO state — what the CEO Console reads to show status/objective/
current task/cycle stage. Kept separate from the orchestrator so the web layer
can poll it without touching business logic."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class CycleStage(str, Enum):
    IDLE = "idle"
    OBSERVE = "observe"
    UNDERSTAND = "understand"
    DECIDE = "decide"
    ACT = "act"
    MEASURE = "measure"
    LEARN = "learn"
    BLOCKED = "blocked"


@dataclass
class CEOState:
    objective: Optional[str] = None
    current_task: Optional[str] = None
    stage: CycleStage = CycleStage.IDLE
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_error: Optional[str] = None

    def set_stage(self, stage: CycleStage, task: Optional[str] = None) -> None:
        self.stage = stage
        if task is not None:
            self.current_task = task
        self.last_updated = datetime.now(timezone.utc)

    def set_objective(self, objective: str) -> None:
        self.objective = objective
        self.last_updated = datetime.now(timezone.utc)

    def set_error(self, error: Optional[str]) -> None:
        self.last_error = error
        self.last_updated = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "objective": self.objective,
            "current_task": self.current_task,
            "stage": self.stage.value,
            "last_updated": self.last_updated.isoformat(),
            "last_error": self.last_error,
        }
