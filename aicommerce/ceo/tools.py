"""Tool definitions the AI CEO's language model can call.

This is the *only* bridge between the LLM and the real system. Every tool
here calls into Company Brain / Control Plane / Orchestrator — the CEO never
gets a raw handle to an agent's client (e.g. the Shopify REST client). Write
actions always go through `propose_action`, which always passes through
Orchestrator.run_cycle (permissions -> budget -> QA -> approval).
"""
from __future__ import annotations

import json
from typing import Any, Callable, Optional

from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord
from aicommerce.brain.tasks import TaskBoard
from aicommerce.brain.tasks import TaskStatus as BoardTaskStatus
from aicommerce.ceo.model_router import ModelRouter
from aicommerce.ceo.orchestrator import Orchestrator, TaskStatus
from aicommerce.ceo.state import CEOState
from aicommerce.ceo.voting import run_technical_vote
from aicommerce.control_plane.scheduler import Scheduler

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
        "name": "get_preflight",
        "description": (
            "Get the ReadinessPreflight report: overall result (ready/blocked/degraded/"
            "requires_approval), which specific checks failed, and why. Call this to explain "
            "*why* something is degraded/blocked instead of guessing — e.g. if asked why "
            "Shopify calls keep failing, or why preflight isn't READY."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_scheduler_status",
        "description": (
            "List every job registered with the Scheduler (name, interval, last run time). "
            "Call this before claiming a scheduled/autonomous job is or isn't running."
        ),
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_recent_events",
        "description": (
            "Read the most recent entries from the EventBus (the real-time control-plane "
            "audit stream: action.executed/denied/failed/qa_rejected/pending_approval, "
            "kill_switch.engaged/disengaged, model.call/model.call_failed). Call this instead "
            "of inferring activity from Company Brain alone when asked what has actually "
            "happened, or to check whether the EventBus itself is live."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "event_type": {"type": "string", "description": "optional exact event type to filter by"},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "generate_status_report",
        "description": (
            "Generate a real CEO status report (Daily Brief / End-of-Day / Executive) from "
            "actual data: preflight, objective, executed/blocked actions in the period, "
            "pending approvals, budget, agents, recent decisions, experiments, problems and "
            "risks. Use this when asked for a status report, daily brief, EOD report, or "
            "executive summary — then narrate it in your own words, but every number and "
            "claim must come from this tool's output, not be invented."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"period": {"type": "string", "enum": ["daily", "eod", "executive"], "default": "daily"}},
        },
    },
    {
        "name": "record_content_brief",
        "description": (
            "Record a structured content brief AFTER Jean has approved a plan that requires "
            "real creative output (a landing page, flyer, product image, video, ad copy, social "
            "post). You and the specialist agents cannot generate that content yourselves -- you "
            "are isolated API calls with no access to Claude Code's real tools (Artifact, Adobe "
            "creative tools, etc.), which only exist in a live conversation with Jean. This tool "
            "does NOT create anything; it writes a clear, structured spec to Company Brain so "
            "Jean can bring it into a conversation with Claude and have it executed for real, "
            "without starting from zero. Only call this for work Jean has actually approved -- "
            "never speculatively."
            "\n\ngeneration_path matters: 'free_local'/'free_api' means Mateo (design) found a "
            "zero-cost path (a local tool, free-tier API, open-source repo) that covers this brief "
            "-- the default, expected case. 'needs_paid_claude_tools' means the free path genuinely "
            "can't deliver what's needed and real cost (Jean's own Claude Code session/tools) is "
            "required -- this case must already have gone through `request_technical_vote` before "
            "you call this tool; say so in approval_reference. Never record 'needs_paid_claude_tools' "
            "speculatively or as a convenience over trying the free path first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "asset_type": {
                    "type": "string",
                    "enum": ["landing_page", "flyer", "product_image", "video", "ad_copy", "social_post", "other"],
                },
                "product": {"type": "string", "description": "which product/offer this is for"},
                "key_message": {"type": "string", "description": "the one thing this asset must communicate"},
                "target_audience": {"type": "string"},
                "generation_path": {
                    "type": "string",
                    "enum": ["free_local", "free_api", "needs_paid_claude_tools"],
                    "default": "free_local",
                    "description": "which path covers this brief -- see tool description",
                },
                "generation_path_reasoning": {
                    "type": "string",
                    "description": "which specific free tool/API/repo was chosen (or why none sufficed)",
                },
                "approval_reference": {
                    "type": "string",
                    "description": "the approval request id or decision that authorized this work -- "
                    "for needs_paid_claude_tools, the request_technical_vote result",
                },
                "notes": {"type": "string", "description": "anything else Claude will need to execute this well"},
            },
            "required": ["asset_type", "product", "key_message"],
        },
    },
    {
        "name": "request_technical_vote",
        "description": (
            "For an important decision, run a real vote: each specialist (Elena/research, "
            "Marcus/store_ops, Priya/engineering_lead) votes FOR/AGAINST/ABSTAIN with real "
            "reasoning on the exact proposal text, through their own 'think' action (real cost, "
            "real memory), PLUS an independent review from Opus (a separate, stronger model with "
            "no stake in the outcome) if configured. This does NOT execute anything and does NOT "
            "replace Jean's approval -- it only produces richer evidence. Use this before "
            "recommending something consequential to Jean, or before proposing a high-risk "
            "action, so what you tell him is backed by more than your own read. Relay the actual "
            "tally and dissent honestly, including if the vote came back AGAINST what you hoped."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "proposal": {
                    "type": "string",
                    "description": "the exact decision/proposal being voted on, stated plainly",
                },
            },
            "required": ["proposal"],
        },
    },
    {
        "name": "provide_missing_config",
        "description": (
            "Apply a configuration value Jean JUST gave you in this conversation, so the system "
            "doesn't stay blocked waiting on a manual .env edit. Use this when you need something "
            "to actually launch (a Shopify store/token, switching PROFILE from 'offline' to "
            "'sandbox' once Jean is ready for real external calls, etc.) -- ask Jean for it "
            "plainly in your own words first, then call this tool ONLY with the exact value he "
            "just typed. NEVER invent, guess, or reuse a value from anywhere else -- if Jean "
            "hasn't given you the value in THIS conversation, you don't have it. Only the keys "
            "listed in the enum are allowed; anything else (API keys to Anthropic/OpenRouter, the "
            "console auth token) is intentionally out of reach of this tool."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "key": {
                    "type": "string",
                    "enum": [
                        "SHOPIFY_STORE",
                        "SHOPIFY_TOKEN",
                        "SHOPIFY_API_VERSION",
                        "PROFILE",
                    ],
                },
                "value": {"type": "string", "description": "the exact value Jean gave you"},
            },
            "required": ["key", "value"],
        },
    },
    {
        "name": "create_task",
        "description": (
            "Create a real, tracked task under an objective, owned by a specific agent. This is "
            "the ONLY way work becomes checkable later -- 'I told Elena to look into X' in chat "
            "is not a task; this is. Use this whenever you delegate something that should be "
            "trackable to completion, not just a one-off question. Group related tasks under the "
            "same `objective` string so progress on a goal can be seen as a whole."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "objective": {"type": "string", "description": "the goal this task belongs to, e.g. 'validate product X'"},
                "title": {"type": "string", "description": "what this specific task is"},
                "owner": {"type": "string", "description": "the agent name actually responsible (e.g. 'research', 'marketing')"},
            },
            "required": ["objective", "title", "owner"],
        },
    },
    {
        "name": "update_task_status",
        "description": (
            "Update a task's real status: pending, in_progress, blocked, done, or cancelled. "
            "Call this the moment status actually changes -- don't let tasks sit stale while you "
            "tell Jean something is 'in progress' in words only. A task already 'done' or "
            "'cancelled' cannot be moved to another status (create a new task instead) -- that's "
            "enforced, not a suggestion. If marking 'blocked', say what it's blocked on in notes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string"},
                "status": {"type": "string", "enum": ["pending", "in_progress", "blocked", "done", "cancelled"]},
                "notes": {"type": "string", "description": "why/what changed, especially for 'blocked'"},
            },
            "required": ["task_id", "status"],
        },
    },
    {
        "name": "list_tasks",
        "description": (
            "List real tasks with their actual current status, optionally filtered by objective, "
            "owner, or status. Use this before telling Jean what's done/pending/blocked, instead "
            "of reconstructing it from memory or chat history -- this is the ground truth."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "objective": {"type": "string"},
                "owner": {"type": "string"},
                "status": {"type": "string", "enum": ["pending", "in_progress", "blocked", "done", "cancelled"]},
            },
        },
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
            "read_products -> {\"limit\": int, \"status\": \"any\"|\"active\"|\"draft\"}. "
            "\n\nagent_name='engineering' (this repository's own code, sandboxed): "
            "current_branch -> {}; read_file -> {\"path\": str}; list_files -> {\"pattern\": str} "
            "(glob, e.g. \"aicommerce/**/*.py\"); git_status -> {}; git_diff -> {\"against\": str}; "
            "run_tests -> {} (runs the real pytest suite, can take a while); "
            "create_branch -> {\"name\": str} (name must NOT be master/main) -- do this BEFORE "
            "write_file or commit, which both refuse to run on master/main; "
            "write_file -> {\"path\": str, \"content\": str}; commit -> {\"message\": str}. "
            "All of the above are low-risk/reversible (local git only, no push exists) and should "
            "be proposed with risk='low', reversible=True. "
            "merge_to_master -> {\"branch\": str} is DIFFERENT: it is hardcoded high-risk at the "
            "control-plane level (Orchestrator forces it to pending_approval regardless of what "
            "risk/reversible you pass) because it's the only path from a sandbox branch into "
            "master. Always run_tests and git_diff first so the approval request Jean sees is "
            "backed by evidence you actually checked, not just a request to trust you."
            "\n\nagent_name='research' is Elena Voss, Senior Market Research Lead -- a real "
            "specialist with her own judgment, not another tool. Delegate open-ended research/"
            "analysis to her instead of doing it yourself (give her the actual question/context, "
            "not just a keyword). She has her own memory (tagged to her, persists across tasks) "
            "and will push back on weak evidence rather than agreeing with whatever you proposed "
            "-- that disagreement is useful, report it to Jean rather than smoothing it over."
            "\n\nagent_name='store_ops' is Marcus Chen, Head of Store Operations -- delegate "
            "catalog strategy, pricing/margin, and fulfillment-capacity judgment to him the same "
            "way. He will refuse to bless a listing plan that assumes supply/fulfillment that "
            "hasn't been proven."
            "\n\nagent_name='engineering_lead' is Priya Nair, Lead Backend Engineer -- delegate "
            "technical/architecture judgment to her the same way BEFORE directing the "
            "'engineering' tool agent to actually touch code, especially for anything "
            "non-trivial. She decides the approach; 'engineering' executes the git/test "
            "mechanics of whatever she (or you) directed."
            "\n\nagent_name='marketing' is Sofia Reyes, Head of Performance Marketing & Growth -- "
            "delegate campaign structure, channel/targeting strategy, and creative-angle direction "
            "to her. She has no ad-account access of her own: any real spend she proposes still "
            "requires `request_technical_vote` and your approval, same as every other cost-bearing "
            "decision. She works from Elena's research, not her own invented market read."
            "\n\nagent_name='design' is Mateo Fonseca, Creative Director (Visual & Ad Design) -- "
            "delegate creative-brief direction to him for ads/store visuals. He cannot generate "
            "actual image/video files himself; his real output is a brief recorded via "
            "`record_content_brief` for Jean/Claude Code to execute. Never report a design task as "
            "'done' based on his think output alone -- it is a brief, not a finished asset."
            "\n\nagent_name='rnd' is Noor Kaelin, Head of R&D & Future Strategy -- delegate "
            "'what else could this company/team become' exploration to them: new business lines "
            "or fields this same team's skills could run, not new products for the current store "
            "(that's Elena). Noor's output is always a labeled HYPOTHESIS for Elena to validate, "
            "never a conclusion -- relay it as exactly that, never as something already decided, "
            "and never let it skip Elena's validation or Nadia's spend-gating."
            "\n\nIMPORTANT -- which action to use for research/store_ops/engineering_lead/"
            "marketing/design/rnd: action='think_background' -> {\"prompt\": str} is the DEFAULT for "
            "routine, day-to-day delegation (this is what '24/7' actually means here) -- it runs "
            "on a free open-weight model, costs ~$0, but is noticeably weaker reasoning. Use "
            "action='think' -> {\"prompt\": str} (the paid, stronger model) only when the matter "
            "is genuinely important enough that you'd also consider `request_technical_vote` for "
            "it -- don't default to the paid path for ordinary work. risk='low', reversible=True, "
            "cost=0 for both (real cost, if any, is metered and charged automatically after the "
            "call)."
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

    def __init__(
        self,
        orchestrator: Orchestrator,
        state: CEOState,
        scheduler: Optional[Scheduler] = None,
        preflight_provider: Optional[Callable[[], Any]] = None,
        opus_router: Optional[ModelRouter] = None,
        voter_agent_names: tuple[str, ...] = (
            "research", "store_ops", "engineering_lead", "finance", "marketing", "design", "rnd",
        ),
        tasks: Optional[TaskBoard] = None,
    ) -> None:
        self.orchestrator = orchestrator
        self.state = state
        self.scheduler = scheduler
        self.preflight_provider = preflight_provider
        self.opus_router = opus_router
        self.voter_agent_names = voter_agent_names
        self.tasks = tasks

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

    def _tool_get_preflight(self) -> dict:
        if self.preflight_provider is None:
            return {"error": "no preflight provider wired into this CEO instance"}
        report = self.preflight_provider()
        return {
            "result": report.result.value,
            "failed_checks": report.failed_checks,
            "reasons": report.reasons,
        }

    def _tool_get_scheduler_status(self) -> dict:
        if self.scheduler is None:
            return {"error": "no scheduler wired into this CEO instance"}
        return {
            "jobs": [
                {
                    "name": j.name,
                    "interval_seconds": j.interval.total_seconds(),
                    "last_run": j.last_run.isoformat() if j.last_run else None,
                }
                for j in self.scheduler.jobs()
            ]
        }

    def _tool_get_recent_events(self, event_type: str | None = None, limit: int = 20) -> dict:
        if self.orchestrator.events is None:
            return {"error": "no EventBus wired into this orchestrator"}
        events = self.orchestrator.events.history(event_type, limit=limit)
        return {
            "events": [
                {"type": e.type, "payload": e.payload, "timestamp": e.timestamp.isoformat()}
                for e in events
            ]
        }

    def _tool_generate_status_report(self, period: str = "daily") -> dict:
        if self.preflight_provider is None:
            return {"error": "no preflight provider wired into this CEO instance"}
        from aicommerce.reports import generate_status_report

        report = generate_status_report(
            self.orchestrator, self.state, self.preflight_provider(), period=period
        )
        return report.to_dict()

    def _tool_record_content_brief(
        self,
        asset_type: str,
        product: str,
        key_message: str,
        target_audience: str = "",
        generation_path: str = "free_local",
        generation_path_reasoning: str = "",
        approval_reference: str = "",
        notes: str = "",
    ) -> dict:
        brief = {
            "asset_type": asset_type,
            "product": product,
            "key_message": key_message,
            "target_audience": target_audience,
            "generation_path": generation_path,
            "generation_path_reasoning": generation_path_reasoning,
            "approval_reference": approval_reference,
            "notes": notes,
            "status": "pending_execution",
        }
        record = MemoryRecord(
            kind=MemoryKind.DECISION,
            content=(
                f"CONTENT BRIEF [{asset_type}] for {product}: {key_message} "
                f"(path: {generation_path})"
                + (f" (audience: {target_audience})" if target_audience else "")
                + (f" (ref: {approval_reference})" if approval_reference else "")
            ),
            source="ai_ceo",
            confidence=Confidence.FACT,
            tags=("content_brief", asset_type, generation_path),
            metadata=brief,
        )
        self.orchestrator.brain.record(record)
        return {"recorded_id": record.id, "status": "pending_execution", **brief}

    def _tool_request_technical_vote(self, proposal: str) -> dict:
        from aicommerce import config

        registered_voters = [
            name for name in self.voter_agent_names if self.orchestrator.registry.get_instance(name) is not None
        ]
        vote = run_technical_vote(
            proposal, self.orchestrator, registered_voters,
            opus_router=self.opus_router, opus_weight=config.OPUS_VOTE_WEIGHT,
        )

        self.orchestrator.brain.record(
            MemoryRecord(
                kind=MemoryKind.DECISION,
                content=vote.summary_text(),
                source="technical_vote",
                confidence=Confidence.FACT,
                tags=("technical_vote",),
                metadata={"tally": vote.tally, "weighted_tally": vote.weighted_tally, "total_cost": vote.total_cost},
            )
        )
        return vote.to_dict()

    _SELF_SERVICE_CONFIG_KEYS = frozenset(
        {"SHOPIFY_STORE", "SHOPIFY_TOKEN", "SHOPIFY_API_VERSION", "PROFILE"}
    )

    def _tool_provide_missing_config(self, key: str, value: str) -> dict:
        from dotenv import set_key

        from aicommerce import config

        if key not in self._SELF_SERVICE_CONFIG_KEYS:
            return {"error": f"'{key}' is not a self-service key. Allowed: {sorted(self._SELF_SERVICE_CONFIG_KEYS)}"}

        if key == "PROFILE" and value not in ("offline", "sandbox", "live"):
            return {"error": "PROFILE must be one of: offline, sandbox, live"}

        set_key(str(config.ENV_PATH), key, value)
        setattr(config, key, value)

        applied_live = False
        shopify_agent = self.orchestrator.registry.get_instance("shopify")
        if shopify_agent is not None:
            if key == "SHOPIFY_STORE":
                shopify_agent.store = value
                applied_live = True
            elif key == "SHOPIFY_TOKEN":
                shopify_agent.token = value
                applied_live = True
            elif key == "SHOPIFY_API_VERSION":
                shopify_agent.api_version = value
                applied_live = True
        if key == "PROFILE":
            applied_live = True  # ShopifyAgent reads config.PROFILE live, no restart needed

        is_secret = "TOKEN" in key or "KEY" in key or "SECRET" in key
        self.orchestrator.brain.record(
            MemoryRecord(
                kind=MemoryKind.DECISION,
                content=f"Jean provided config value for {key} (applied_live={applied_live})"
                + ("" if is_secret else f": {value}"),
                source="ai_ceo",
                confidence=Confidence.FACT,
                tags=("config_update", key),
            )
        )
        return {"key": key, "applied_live": applied_live, "status": "ok"}

    def _require_tasks(self) -> Optional[dict]:
        if self.tasks is None:
            return {"error": "no TaskBoard wired into this CEO instance"}
        return None

    def _tool_create_task(self, objective: str, title: str, owner: str) -> dict:
        if (err := self._require_tasks()) is not None:
            return err
        task = self.tasks.create(objective=objective, title=title, owner=owner)
        return {
            "id": task.id, "objective": task.objective, "title": task.title,
            "owner": task.owner, "status": task.status.value,
        }

    def _tool_update_task_status(self, task_id: str, status: str, notes: str = "") -> dict:
        if (err := self._require_tasks()) is not None:
            return err
        try:
            task = self.tasks.update_status(task_id, BoardTaskStatus(status), notes=notes)
        except KeyError as exc:
            return {"error": str(exc)}
        except ValueError as exc:  # InvalidTaskTransition
            return {"error": str(exc)}
        return {
            "id": task.id, "objective": task.objective, "title": task.title,
            "owner": task.owner, "status": task.status.value, "notes": task.notes,
        }

    def _tool_list_tasks(
        self, objective: str = "", owner: str = "", status: str = ""
    ) -> dict:
        if (err := self._require_tasks()) is not None:
            return err
        tasks = self.tasks.list(
            objective=objective or None,
            owner=owner or None,
            status=BoardTaskStatus(status) if status else None,
        )
        return {
            "tasks": [
                {
                    "id": t.id, "objective": t.objective, "title": t.title,
                    "owner": t.owner, "status": t.status.value, "notes": t.notes,
                }
                for t in tasks
            ]
        }

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
