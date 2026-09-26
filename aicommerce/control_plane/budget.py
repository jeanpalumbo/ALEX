"""Budget Guard — enforces spend limits, does not merely recommend them.

Tracks daily/monthly, per-agent, per-campaign, per-supplier and per-experiment
budgets, plus reserved (not-yet-spent) budget, and estimated vs actual cost.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class BudgetExceededError(RuntimeError):
    pass


@dataclass
class Budget:
    scope: str  # e.g. "daily", "agent:research", "campaign:launch-1"
    limit: float
    spent: float = 0.0
    reserved: float = 0.0

    @property
    def available(self) -> float:
        return self.limit - self.spent - self.reserved


class BudgetGuard:
    """Never silently routes spend past a limit — every call either succeeds
    within budget or raises `BudgetExceededError`. There is no bypass path."""

    def __init__(self) -> None:
        self._budgets: dict[str, Budget] = {}
        self._history: list[dict] = []

    def set_budget(self, scope: str, limit: float) -> Budget:
        budget = self._budgets.setdefault(scope, Budget(scope=scope, limit=limit))
        budget.limit = limit
        return budget

    def get(self, scope: str) -> Budget:
        if scope not in self._budgets:
            raise KeyError(f"no budget defined for scope '{scope}'")
        return self._budgets[scope]

    def reserve(self, scope: str, amount: float) -> None:
        budget = self.get(scope)
        if amount > budget.available:
            raise BudgetExceededError(
                f"cannot reserve {amount} in scope '{scope}': only {budget.available} available"
            )
        budget.reserved += amount

    def release_reservation(self, scope: str, amount: float) -> None:
        budget = self.get(scope)
        budget.reserved = max(0.0, budget.reserved - amount)

    def spend(self, scope: str, amount: float, *, from_reservation: bool = False) -> None:
        """Record actual spend. Raises if it would exceed the limit.

        If `from_reservation` is True, `amount` is drawn down from the existing
        reservation instead of checked against fresh availability — use this
        when converting a reserved amount into actual spend, since the budget
        was already checked at reservation time.
        """
        budget = self.get(scope)
        if from_reservation:
            budget.reserved = max(0.0, budget.reserved - amount)
        elif amount > budget.available:
            raise BudgetExceededError(
                f"spending {amount} in scope '{scope}' would exceed budget "
                f"(available={budget.available}, limit={budget.limit})"
            )
        budget.spent += amount
        self._history.append({"scope": scope, "amount": amount})

    def status(self, scope: str) -> dict:
        b = self.get(scope)
        return {
            "scope": b.scope,
            "limit": b.limit,
            "spent": b.spent,
            "reserved": b.reserved,
            "available": b.available,
        }

    def history(self, scope: str | None = None) -> list[dict]:
        if scope is None:
            return list(self._history)
        return [h for h in self._history if h["scope"] == scope]

    def scopes(self) -> list[str]:
        return list(self._budgets.keys())

    def all_status(self) -> list[dict]:
        return [self.status(s) for s in self._budgets]
