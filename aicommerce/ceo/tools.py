"""Tool definitions the AI CEO's language model can call.

This is the *only* bridge between the LLM and the real system. Every tool
here calls into Company Brain / Control Plane / Orchestrator — the CEO never
gets a raw handle to an agent's client (e.g. the Shopify REST client). Write
actions always go through `propose_action`, which always passes through
Orchestrator.run_cycle (permissions -> budget -> QA -> approval).
"""
from __future__ import annotations

import json
from typing import Any, Callable

from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord
from aicommerce.ceo.orchestrator import Orchestrator, TaskStatus
from aicommerce.ceo.state import CEOState

TOOL_SCHEMAS: list[dict] = [
    {
        "name": "get_company_state",
        "description": (
            "Get the AI CEO's current objective, current task, cycle stage, "
            "budget status for every known scope, count of pending approvals, "
            "and the list of registered agents. Call this before answering any "
            "question about 'what are you doing' or 'what is the state of the company'."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "query_memory",
        "description": (
            "Read from the Company Brain (persistent organizational memory). "
            "Use this instead of guessing when asked what the company knows, "
            "has decided, or has learned. kind must be one of: episodic, "
            "semantic, procedural, decision, experiment, institutional."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": [k.value for k in MemoryKind]},
                "tags": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "record_memory",
        "description": (
            "Write an entry to the Company Brain. Always set `confidence` "
            "honestly: fact (verified), inference (derived), hypothesis "
            "(unverified assumption), or unknown. Never record a hypothesis as fact."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "kind": {
                    "type": "string",
                    "enum": [k.value for k in MemoryKind if k != MemoryKind.INSTITUTIONAL],
                    "description": "institutional memory is reserved for human-authored constitution/rules, not for the CEO to write.",
                },
                "content": {"type": "string"},
                "confidence": {"type": "string", "enum": [c.value for c in Confidence]},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["kind", "content", "confidence"],
        },
    },
    {
        "name": "list_agents",
        "description": "List every agent registered in the control plane, with its mission, tools and limits.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_pending_approvals",
        "description": "List actions currently waiting on human approval.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "set_objective",
        "description": "Set the CEO's current stated objective, shown on the console.",
        "input_schema": {"type": "object", "properties": {"objective": {"type": "string"}}, "required": ["objective"]},
    },
    {
        "name": "propose_action",
        "description": (
            "Propose that a registered agent perform an action. This is the ONLY way "
            "to make anything actually happen (read Shopify data, write Shopify data, etc.). "
            "It always goes through permission checks, budget checks, QA and — for "
            "risk='high'/'critical' or reversible=False — human approval. A write action "
            "(e.g. shopify create_product/update_product/set_price/set_inventory/delete_product) "
            "MUST be proposed with risk='high' and reversible=False unless you have a specific "
            "reason not to; a read action (read_products/read_orders/read_customers/read_shop/"
            "read_inventory/read_product/read_order) should use risk='low', reversible=True, cost=0. "
            "Shopify action params must be nested exactly as the agent expects: "
            "create_product -> {\"product_data\": {\"title\": ..., \"body_html\": ..., \"vendor\": ..., ...}}; "
            "update_product -> {\"product_id\": int, \"updates\": {...}}; "
            "set_price -> {\"variant_id\": int, \"price\": \"9.99\"}; "
            "set_inventory -> {\"inventory_item_id\": int, \"location_id\": int, \"available\": int}; "
            "delete_product -> {\"product_id\": int}; "
            "read_products -> {\"limit\": int, \"status\": \"any\"|\"active\"|\"draft\"}."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_name": {"type": "string"},
                "action": {"type": "string"},
                "params": {"type": "object", "description": "action-specific parameters, e.g. {\"limit\": 10} for read_products"},
                "cost": {"type": "number", "default": 0},
                "risk": {"type": "string", "enum": ["low", "medium", "high", "critical"], "default": "low"},
                "reversible": {"type": "boolean", "default": True},
            },
            "required": ["agent_name", "action"],
        },
    },
]


class CEOTools:
    """Binds the tool schemas above to real callables against a live system."""

    def __init__(self, orchestrator: Orchestrator, state: CEOState) -> None:
        self.orchestrator = orchestrator
        self.state = state

    def dispatch(self, name: str, tool_input: dict) -> Any:
        handler: Callable[..., Any] = getattr(self, f"_tool_{name}", None)
        if handler is None:
            return {"error": f"unknown tool '{name}'"}
        try:
            return handler(**tool_input)
        except Exception as exc:  # noqa: BLE001 — a tool error is data for the model, not a crash
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    def _tool_get_company_state(self) -> dict:
        return {
            "ceo_state": self.state.to_dict(),
            "budgets": self.orchestrator.budget.all_status(),
            "pending_approvals": len(self.orchestrator.approvals.pending()),
            "agents": [s.name for s in self.orchestrator.registry.list_agents()],
        }

    def _tool_query_memory(self, kind: str | None = None, tags: list[str] | None = None, limit: int = 20) -> dict:
        records = self.orchestrator.brain.query(
            kind=MemoryKind(kind) if kind else None, tags=tags, limit=limit
        )
        return {
            "records": [
                {
                    "id": r.id,
                    "kind": r.kind.value,
                    "content": r.content,
                    "source": r.source,
                    "confidence": r.confidence.value,
                    "tags": list(r.tags),
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in records
            ]
        }

    def _tool_record_memory(self, kind: str, content: str, confidence: str, tags: list[str] | None = None) -> dict:
        record = MemoryRecord(
            kind=MemoryKind(kind),
            content=content,
            source="ai_ceo",
            confidence=Confidence(confidence),
            tags=tuple(tags or ()),
        )
        self.orchestrator.brain.record(record)
        return {"recorded_id": record.id}

    def _tool_list_agents(self) -> dict:
        return {
            "agents": [
                {
                    "name": s.name,
                    "mission": s.mission,
                    "tools": list(s.tools),
                    "limits": s.limits,
                    "kpis": list(s.kpis),
                }
                for s in self.orchestrator.registry.list_agents()
            ]
        }

    def _tool_get_pending_approvals(self) -> dict:
        return {
            "pending": [
                {
                    "id": r.id,
                    "action": r.action,
                    "agent": r.agent,
                    "reason": r.reason,
                    "cost": r.cost,
                    "risk": r.risk,
                    "reversible": r.reversible,
                    "proposal": r.proposal,
                }
                for r in self.orchestrator.approvals.pending()
            ]
        }

    def _tool_set_objective(self, objective: str) -> dict:
        self.state.set_objective(objective)
        self.orchestrator.brain.record(
            MemoryRecord(
                kind=MemoryKind.DECISION,
                content=f"CEO objective set: {objective}",
                source="ai_ceo",
                confidence=Confidence.FACT,
                tags=("objective",),
            )
        )
        return {"ok": True}

    def _tool_propose_action(
        self,
        agent_name: str,
        action: str,
        params: dict | None = None,
        cost: float = 0.0,
        risk: str = "low",
        reversible: bool = True,
    ) -> dict:
        self.state.set_stage(self.state.stage, task=f"{agent_name}.{action}")
        budget_scope = agent_name  # one budget scope per agent, kept simple for the MVP
        outcome = self.orchestrator.run_cycle(
            objective=self.state.objective or action,
            agent_name=agent_name,
            action=action,
            budget_scope=budget_scope,
            cost=cost,
            risk=risk,
            reversible=reversible,
            params=params,
        )
        response = {"status": outcome.status.value, "detail": outcome.detail}
        if outcome.approval_request_id:
            response["approval_request_id"] = outcome.approval_request_id
        if outcome.agent_result is not None:
            response["output"] = _jsonable(outcome.agent_result.output)
            response["success"] = outcome.agent_result.success
        return response


def _jsonable(value: Any) -> Any:
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)
