"""Agent registry — the control plane's record of which agents exist and what
they're allowed to do (mission, authority, tools, limits, KPIs, model policy)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentSpec:
    """Declared identity of an agent, per master context section 7.

    This is metadata/governance, not the agent's executable logic (see
    `aicommerce.agents.base.Agent` for that).
    """

    name: str
    mission: str
    authority: tuple[str, ...] = field(default_factory=tuple)  # action scopes it may take
    tools: tuple[str, ...] = field(default_factory=tuple)
    limits: dict = field(default_factory=dict)  # e.g. {"max_spend_per_day": 50}
    escalation_policy: str = "escalate to CEO on failure or risk breach"
    kpis: tuple[str, ...] = field(default_factory=tuple)
    model_policy: str = "tier-1"  # conceptual tier, see master context section 28


class AgentRegistry:
    """In-memory registry of AgentSpec + the live agent instance for each name.

    In-memory only for now: restarting the process forgets registrations
    (marked PARTIAL in the README) — persistence would be the next step.
    """

    def __init__(self) -> None:
        self._specs: dict[str, AgentSpec] = {}
        self._instances: dict[str, object] = {}

    def register(self, spec: AgentSpec, instance: object) -> None:
        if spec.name in self._specs:
            raise ValueError(f"agent '{spec.name}' is already registered")
        self._specs[spec.name] = spec
        self._instances[spec.name] = instance

    def unregister(self, name: str) -> None:
        self._specs.pop(name, None)
        self._instances.pop(name, None)

    def get_spec(self, name: str) -> Optional[AgentSpec]:
        return self._specs.get(name)

    def get_instance(self, name: str):
        return self._instances.get(name)

    def list_agents(self) -> list[AgentSpec]:
        return list(self._specs.values())

    def find_by_tool(self, tool: str) -> list[AgentSpec]:
        return [s for s in self._specs.values() if tool in s.tools]
