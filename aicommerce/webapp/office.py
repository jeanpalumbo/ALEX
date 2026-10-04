"""Real-data adapter for the pixel-art office visualization.

Maps the actual persona roster + real TaskBoard state into the snapshot
shape the office frontend consumes (see `diseno-oficina-agentes.md` /
`claude-handoff-oficina.md` in the design package Jean supplied). No status
or task here is invented: `working`/`idle` is derived strictly from whether
the agent currently owns an `in_progress` task in `TaskBoard` -- the same
real task system built for Jean's "no desorden total" requirement.

Deviation from the original spec, documented rather than silently applied:
the spec assumed 7 persona agents (CEO + 6 specialists). The real roster now
has 8 specialists (Noor/R&D was added after that spec was written) + CEO.
The office reflects the real roster, not the spec's stale count.
"""
from __future__ import annotations

from typing import Any

from aicommerce.agents.persona import CEO_PERSONA
from aicommerce.brain.tasks import TaskStatus

# agent_id (matches TaskBoard `owner` / registry name) -> System attribute
# holding that PersonaAgent. CEO is handled separately (not in the registry).
_PERSONA_AGENT_ATTRS = {
    "research": "research_agent",
    "store_ops": "store_ops_agent",
    "engineering_lead": "engineering_lead_agent",
    "finance": "finance_agent",
    "marketing": "marketing_agent",
    "design": "design_agent",
    "rnd": "rnd_agent",
}


def _agent_snapshot(agent_id: str, display_name: str, role: str, system: Any) -> dict:
    in_progress = system.tasks.list(owner=agent_id, status=TaskStatus.IN_PROGRESS, limit=1)
    if in_progress:
        task = in_progress[0]
        return {
            "agent_id": agent_id,
            "display_name": display_name,
            "role": role,
            "status": "working",
            "task": {"id": task.id, "title": task.title},
            "updated_at": task.updated_at.isoformat(),
        }
    return {
        "agent_id": agent_id,
        "display_name": display_name,
        "role": role,
        "status": "idle",
        "task": None,
        "updated_at": None,
    }


def get_office_agents(system: Any) -> list[dict]:
    agents = [_agent_snapshot("ceo", CEO_PERSONA.name, CEO_PERSONA.role, system)]
    for agent_id, attr_name in _PERSONA_AGENT_ATTRS.items():
        persona_agent = getattr(system, attr_name, None)
        if persona_agent is None:
            continue  # not registered in this System instance -- skip, don't fabricate
        persona = persona_agent.persona
        agents.append(_agent_snapshot(agent_id, persona.name, persona.role, system))
    return agents
