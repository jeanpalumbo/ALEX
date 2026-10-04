"""Wires one live instance of the whole system: Company Brain, control plane,
agents, permissions, budgets, orchestrator, CEO service, scheduler.

This is what both the web server and any future CLI/script should import
instead of constructing these objects themselves, so there is exactly one
source of truth at runtime.
"""
from __future__ import annotations

from datetime import timedelta

from aicommerce import config
from aicommerce.agents.engineering_agent import EngineeringAgent
from aicommerce.agents.persona import (
    ENGINEERING_PERSONA,
    FINANCE_PERSONA,
    RESEARCH_PERSONA,
    STORE_OPS_PERSONA,
    PersonaAgent,
)
from aicommerce.agents.shopify_agent import ShopifyAgent
from aicommerce.agents.stubs import QAAgent
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.llm import CEOModel, OpenRouterModel
from aicommerce.ceo.model_router import ModelRouter
from aicommerce.ceo.orchestrator import Orchestrator
from aicommerce.ceo.service import CEOService
from aicommerce.control_plane.approvals import ApprovalQueue
from aicommerce.control_plane.budget import BudgetGuard
from aicommerce.control_plane.events import EventBus
from aicommerce.control_plane.permissions import PermissionManager, Role
from aicommerce.control_plane.preflight import PreflightResult, ReadinessPreflight
from aicommerce.control_plane.registry import AgentRegistry, AgentSpec
from aicommerce.control_plane.scheduler import Scheduler


class System:
    def __init__(self) -> None:
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)

        self.brain = CompanyBrain(config.BRAIN_DB_PATH)
        self.registry = AgentRegistry()
        self.permissions = PermissionManager()
        self.budget = BudgetGuard()
        self.approvals = ApprovalQueue()
        self.events = EventBus(db_path=config.DATA_DIR / "events.db")
        self.scheduler = Scheduler(db_path=config.DATA_DIR / "scheduler.db")

        self._register_agents()
        self._configure_permissions()
        self._configure_budgets()
        self._wire_events()

        self.orchestrator = Orchestrator(
            self.registry,
            self.permissions,
            self.budget,
            self.approvals,
            self.brain,
            QAAgent(),
            approval_ttl_seconds=config.APPROVAL_TTL_SECONDS,
            events=self.events,
            kill_switch_db_path=config.DATA_DIR / "kill_switch.db",
        )
        self.ceo = CEOService(
            self.orchestrator, CEOModel(), scheduler=self.scheduler, opus_router=self.opus_router
        )
        self.preflight = self._build_preflight()
        self.ceo.tools.preflight_provider = self.preflight.run
        self._configure_scheduler()

    # ------------------------------------------------------------------
    def _register_agents(self) -> None:
        # One shared free-tier router for every persona's autonomous check-ins.
        # Inert (raises LLMNotConfigured on call) until OPENROUTER_API_KEY is
        # set -- see aicommerce/ceo/llm.py:OpenRouterModel.
        self.background_router = ModelRouter(OpenRouterModel(), events=self.events)
        # Independent technical review for important decisions (voting.py) --
        # a real, separate Anthropic call (Opus, not the CEO's own Sonnet),
        # metered on its own budget scope so a vote can't silently drain
        # another scope's spend.
        self.opus_router = ModelRouter(CEOModel(model=config.OPUS_MODEL), events=self.events)

        self.shopify_agent = ShopifyAgent()
        self.registry.register(
            AgentSpec(
                name="shopify",
                mission="Read and (with approval) write the Shopify store's products, "
                "inventory, orders and customers.",
                authority=("read_products", "read_orders", "read_customers", "read_shop", "read_inventory"),
                tools=("shopify_admin_api",),
                limits={"requires_approval_for": "all write actions"},
                kpis=("catalog_accuracy", "order_fulfillment_latency"),
                high_risk_actions=frozenset(ShopifyAgent.WRITE_ACTIONS),
            ),
            self.shopify_agent,
        )

        self.engineering_agent = EngineeringAgent()
        self.registry.register(
            AgentSpec(
                name="engineering",
                mission="Read, edit, test and commit code on a sandbox branch of this "
                "repository. Never touches master directly; merging to master always "
                "requires human approval.",
                authority=tuple(EngineeringAgent.READ_ACTIONS | EngineeringAgent.WRITE_ACTIONS),
                tools=("git", "pytest"),
                limits={"protected_branches": sorted(EngineeringAgent.MERGE_ACTIONS)},
                kpis=("test_pass_rate", "review_turnaround"),
                high_risk_actions=frozenset(EngineeringAgent.MERGE_ACTIONS),
            ),
            self.engineering_agent,
        )

        self.research_agent = PersonaAgent(
            RESEARCH_PERSONA, ModelRouter(CEOModel(), events=self.events), self.brain,
            background_router=self.background_router,
        )
        self.registry.register(
            AgentSpec(
                name="research",
                mission=RESEARCH_PERSONA.mission,
                authority=("think",),
                tools=("anthropic_model",),
                limits={"persona": RESEARCH_PERSONA.name, "role": RESEARCH_PERSONA.role},
                kpis=("recommendation_accuracy", "evidence_quality"),
            ),
            self.research_agent,
        )

        self.store_ops_agent = PersonaAgent(
            STORE_OPS_PERSONA, ModelRouter(CEOModel(), events=self.events), self.brain,
            background_router=self.background_router,
        )
        self.registry.register(
            AgentSpec(
                name="store_ops",
                mission=STORE_OPS_PERSONA.mission,
                authority=("think",),
                tools=("anthropic_model",),
                limits={"persona": STORE_OPS_PERSONA.name, "role": STORE_OPS_PERSONA.role},
                kpis=("margin_accuracy", "stockout_rate"),
            ),
            self.store_ops_agent,
        )

        self.engineering_lead_agent = PersonaAgent(
            ENGINEERING_PERSONA, ModelRouter(CEOModel(), events=self.events), self.brain,
            background_router=self.background_router,
        )
        self.registry.register(
            AgentSpec(
                name="engineering_lead",
                mission=ENGINEERING_PERSONA.mission,
                authority=("think",),
                tools=("anthropic_model",),
                limits={"persona": ENGINEERING_PERSONA.name, "role": ENGINEERING_PERSONA.role},
                kpis=("regression_rate", "review_quality"),
            ),
            self.engineering_lead_agent,
        )

        self.finance_agent = PersonaAgent(
            FINANCE_PERSONA, ModelRouter(CEOModel(), events=self.events), self.brain,
            background_router=self.background_router,
        )
        self.registry.register(
            AgentSpec(
                name="finance",
                mission=FINANCE_PERSONA.mission,
                authority=("think",),
                tools=("anthropic_model",),
                limits={"persona": FINANCE_PERSONA.name, "role": FINANCE_PERSONA.role},
                kpis=("spend_discipline", "runway_accuracy"),
            ),
            self.finance_agent,
        )

    def _configure_permissions(self) -> None:
        self.permissions.define_role(
            Role(
                name="shopify_read",
                allowed_actions=frozenset(ShopifyAgent.READ_ACTIONS),
                allowed_tools=frozenset({"shopify_admin_api"}),
            )
        )
        self.permissions.define_role(
            Role(
                name="shopify_write",
                allowed_actions=frozenset(ShopifyAgent.WRITE_ACTIONS),
                allowed_tools=frozenset({"shopify_admin_api"}),
            )
        )
        self.permissions.assign_role("shopify", "shopify_read")
        self.permissions.assign_role("shopify", "shopify_write")

        self.permissions.define_role(
            Role(
                name="engineering_full",
                allowed_actions=frozenset(
                    EngineeringAgent.READ_ACTIONS | EngineeringAgent.WRITE_ACTIONS | EngineeringAgent.MERGE_ACTIONS
                ),
                allowed_tools=frozenset({"git", "pytest"}),
            )
        )
        self.permissions.assign_role("engineering", "engineering_full")

        self.permissions.define_role(
            Role(
                name="persona_think",
                allowed_actions=frozenset({"think", "think_background"}),
                allowed_tools=frozenset({"anthropic_model"}),
            )
        )
        self.permissions.assign_role("research", "persona_think")
        self.permissions.assign_role("store_ops", "persona_think")
        self.permissions.assign_role("engineering_lead", "persona_think")
        self.permissions.assign_role("finance", "persona_think")

    def _configure_budgets(self) -> None:
        self.budget.set_budget("daily", config.DAILY_BUDGET_LIMIT)
        self.budget.set_budget("shopify", config.SHOPIFY_BUDGET_LIMIT)
        self.budget.set_budget("ceo_llm", config.CEO_LLM_BUDGET_LIMIT)
        self.budget.set_budget("engineering", config.ENGINEERING_BUDGET_LIMIT)
        self.budget.set_budget("research", config.RESEARCH_BUDGET_LIMIT)
        self.budget.set_budget("store_ops", config.STORE_OPS_BUDGET_LIMIT)
        self.budget.set_budget("engineering_lead", config.ENGINEERING_LEAD_BUDGET_LIMIT)
        self.budget.set_budget("finance", config.FINANCE_BUDGET_LIMIT)
        self.budget.set_budget("opus_review", config.OPUS_REVIEW_BUDGET_LIMIT)

    def _wire_events(self) -> None:
        self.events.subscribe("approval.required", lambda e: None)  # placeholder hook point

    def _build_preflight(self) -> ReadinessPreflight:
        pf = ReadinessPreflight()
        pf.add_check(
            "ceo_llm_configured",
            lambda: self.ceo.llm_configured,
            on_fail=PreflightResult.BLOCKED,
            reason="ANTHROPIC_API_KEY not set — CEO chat is disabled",
        )
        pf.add_check(
            "shopify_configured",
            lambda: self.shopify_agent.configured,
            on_fail=PreflightResult.DEGRADED,
            reason="SHOPIFY_STORE/SHOPIFY_TOKEN not set — Shopify agent will fail on any call",
        )
        pf.add_check(
            "profile_allows_external_calls",
            lambda: config.PROFILE != "offline",
            on_fail=PreflightResult.DEGRADED,
            reason=f"PROFILE={config.PROFILE} — no agent may make real external calls until "
            "PROFILE is set to sandbox or live",
        )
        pf.add_check(
            "kill_switch_not_engaged",
            lambda: not self.orchestrator.kill_switch_engaged,
            on_fail=PreflightResult.BLOCKED,
            reason="kill switch is engaged — see /api/killswitch for the reason",
        )
        return pf

    def _configure_scheduler(self) -> None:
        def heartbeat() -> None:
            from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord

            report = self.preflight.run()
            self.brain.record(
                MemoryRecord(
                    kind=MemoryKind.EPISODIC,
                    content=f"Scheduler heartbeat. Preflight={report.result.value}. "
                    f"Pending approvals={len(self.approvals.pending())}.",
                    source="scheduler",
                    confidence=Confidence.FACT,
                    tags=("heartbeat",),
                )
            )

        self.scheduler.add_job("heartbeat", timedelta(minutes=15), heartbeat)

        if config.AUTONOMOUS_LLM_TICKS:
            def autonomous_tick() -> None:
                self.budget.reserve("ceo_llm", config.AUTONOMOUS_TICK_ESTIMATED_COST)
                try:
                    self.ceo.chat(
                        "This is an autonomous scheduler tick, not a message from Jean. "
                        "Check company state and pending approvals; record any notable "
                        "observation to memory. Do not propose spend-incurring actions "
                        "unless something is clearly wrong."
                    )
                finally:
                    self.budget.spend(
                        "ceo_llm", config.AUTONOMOUS_TICK_ESTIMATED_COST, from_reservation=True
                    )

            self.scheduler.add_job(
                "autonomous_ceo_tick",
                timedelta(seconds=config.AUTONOMOUS_TICK_INTERVAL_SECONDS),
                autonomous_tick,
            )

        if config.AUTONOMOUS_PERSONA_TICKS:
            self._configure_persona_autonomy()

    def _configure_persona_autonomy(self) -> None:
        """Each persona checks in on its own schedule instead of only acting
        when the CEO explicitly delegates to it -- this is what makes them
        "working 24/7" rather than purely reactive. Still goes through
        Orchestrator.run_cycle like any other action: same budget scope,
        same permission check, same audit trail, same event publishing.
        Nothing here grants a persona new authority -- `think` was already
        its only permitted action; this just calls it on a timer too."""
        checkins = {
            "research": (
                "Autonomous check-in, not a message from Jean. Review the CEO's current "
                "objective (if any) and your own memory. If there's a real market/pricing/"
                "competitive question relevant to the current objective that you haven't "
                "already answered, give your professional read on it now, tagged FACT/"
                "INFERENCE/HYPOTHESIS/UNKNOWN as always. If there's nothing new to add since "
                "your last check-in, say so briefly -- do not manufacture busywork."
            ),
            "store_ops": (
                "Autonomous check-in, not a message from Jean. Review the CEO's current "
                "objective and your own memory for anything store-operations-relevant "
                "(catalog readiness, pricing/margin concerns, fulfillment risk). If nothing "
                "has changed since your last check-in, say so briefly rather than restating "
                "old findings as if they were new."
            ),
            "engineering_lead": (
                "Autonomous check-in, not a message from Jean. Review recent engineering "
                "activity (ask the engineering tool agent's own history via your memory) for "
                "anything worth flagging -- risk, tech debt, a change that deserved more "
                "scrutiny. If there's nothing new, say so briefly."
            ),
            "finance": (
                "Autonomous check-in, not a message from Jean. Review current budget status "
                "and recent spend across every scope, and the CEO's current objective. Flag "
                "anything that looks like spend creeping in before it was validated for free, "
                "or any budget scope trending toward its limit. The company's default right now "
                "is $0 real spend until something shows real traction -- if everything is still "
                "at $0 or trivial, say so briefly rather than manufacturing a concern."
            ),
        }

        for agent_name, prompt in checkins.items():
            def make_tick(agent_name: str, prompt: str):
                def tick() -> None:
                    outcome = self.orchestrator.run_cycle(
                        objective=self.ceo.state.objective or "autonomous persona check-in",
                        agent_name=agent_name,
                        action="think_background",
                        budget_scope=agent_name,
                        cost=0.0,  # free-tier model: real cost is $0, or it fails cleanly if unconfigured
                        risk="low",
                        reversible=True,
                        params={"prompt": prompt},
                    )
                    if outcome.status.value != "executed":
                        from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord

                        self.brain.record(
                            MemoryRecord(
                                kind=MemoryKind.EPISODIC,
                                content=f"Autonomous check-in for '{agent_name}' did not execute: "
                                f"{outcome.status.value} — {outcome.detail}",
                                source="scheduler",
                                confidence=Confidence.FACT,
                                tags=("autonomous_tick", agent_name),
                            )
                        )

                return tick

            self.scheduler.add_job(
                f"autonomous_{agent_name}_tick",
                timedelta(seconds=config.AUTONOMOUS_PERSONA_TICK_INTERVAL_SECONDS),
                make_tick(agent_name, prompt),
            )


_system: System | None = None


def get_system() -> System:
    global _system
    if _system is None:
        _system = System()
    return _system
