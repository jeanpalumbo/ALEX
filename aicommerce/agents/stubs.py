"""Stub agents — enough real behavior to exercise the orchestrator loop and be
unit-tested, but no external API calls. These are wiring, not the real
Research/Product/Brand/... agents described in the master context.
"""
from __future__ import annotations

from .base import Agent, AgentResult


class EchoAgent(Agent):
    """Generic stand-in worker: 'does' a task by recording what it would do.

    Useful until a real specialized agent (Research, Product, ...) replaces it
    for a given task type.
    """

    def __init__(self, name: str, cost_per_task: float = 0.0) -> None:
        self.name = name
        self.cost_per_task = cost_per_task

    def execute(self, task: dict) -> AgentResult:
        objective = task.get("objective", "<no objective given>")
        return AgentResult(
            success=True,
            output=f"[{self.name}] would perform: {objective}",
            cost=self.cost_per_task,
            evidence=f"stub agent '{self.name}' executed synchronously, no external call made",
        )


class QAAgent(Agent):
    """Validates another agent's AgentResult against simple, explicit rules.

    Implements the "Agent -> QA -> Approval -> Execute" pattern from the
    master context: nothing downstream trusts agent output without a QA pass.
    """

    name = "qa"

    def review(self, result: AgentResult) -> AgentResult:
        if not result.success:
            return AgentResult(success=False, error="upstream agent reported failure")
        if not result.evidence:
            return AgentResult(success=False, error="no evidence attached to result — cannot validate")
        return AgentResult(success=True, output="QA passed", evidence="evidence field present and upstream reported success")

    def execute(self, task: dict) -> AgentResult:
        result = task.get("result")
        if not isinstance(result, AgentResult):
            return AgentResult(success=False, error="QAAgent.execute requires task['result'] to be an AgentResult")
        return self.review(result)
