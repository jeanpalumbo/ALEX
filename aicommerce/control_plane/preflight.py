"""Readiness Preflight — verify required tools/auth/permissions/budget/services
/data/config/limits/risk before an important action runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class PreflightResult(str, Enum):
    READY = "ready"
    BLOCKED = "blocked"
    DEGRADED = "degraded"
    REQUIRES_APPROVAL = "requires_approval"


@dataclass
class PreflightCheck:
    name: str
    check: Callable[[], bool]
    on_fail: PreflightResult
    reason: str = ""


@dataclass
class PreflightReport:
    result: PreflightResult
    failed_checks: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)


class ReadinessPreflight:
    """A named set of checks. Worst-outcome-wins: if any check fails, its
    `on_fail` result is used; BLOCKED outranks REQUIRES_APPROVAL outranks
    DEGRADED. Only if every check passes is the result READY.
    """

    _SEVERITY = {
        PreflightResult.BLOCKED: 3,
        PreflightResult.REQUIRES_APPROVAL: 2,
        PreflightResult.DEGRADED: 1,
        PreflightResult.READY: 0,
    }

    def __init__(self) -> None:
        self._checks: list[PreflightCheck] = []

    def add_check(
        self,
        name: str,
        check: Callable[[], bool],
        on_fail: PreflightResult = PreflightResult.BLOCKED,
        reason: str = "",
    ) -> None:
        self._checks.append(PreflightCheck(name=name, check=check, on_fail=on_fail, reason=reason))

    def run(self) -> PreflightReport:
        worst = PreflightResult.READY
        failed: list[str] = []
        reasons: list[str] = []
        for c in self._checks:
            try:
                passed = bool(c.check())
            except Exception as exc:  # a raising check counts as failed, not a crash
                passed = False
                c = PreflightCheck(c.name, c.check, c.on_fail, reason=f"check raised: {exc}")
            if not passed:
                failed.append(c.name)
                if c.reason:
                    reasons.append(c.reason)
                if self._SEVERITY[c.on_fail] > self._SEVERITY[worst]:
                    worst = c.on_fail
        return PreflightReport(result=worst, failed_checks=failed, reasons=reasons)
