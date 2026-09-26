"""Wires one live instance of the whole system: Company Brain, control plane,
agents, permissions, budgets, orchestrator, CEO service, scheduler.

This is what both the web server and any future CLI/script should import
instead of constructing these objects themselves, so there is exactly one
source of truth at runtime.
"""
from __future__ import annotations

from datetime import timedelta

from aicommerce import config
from aicommerce.agents.shopify_agent import ShopifyAgent
from aicommerce.agents.stubs import QAAgent
from aicommerce.brain.store import CompanyBrain
from aicommerce.ceo.llm import CEOModel
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
        self.events = EventBus()
        self.scheduler = Scheduler()

        self._register_agents()
        self._configure_permissions()
        self._configure_budgets()
        self._wire_events()

        self.orchestrator = Orchestrator(
            self.registry, self.permissions, self.budget, self.approvals, self.brain, QAAgent()
        )
        self.ceo = CEOService(self.orchestrator, CEOModel())
        self.preflight = self._build_preflight()
        self._configure_scheduler()

    # ------------------------------------------------------------------
    def _register_agents(self) -> None:
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
            ),
            self.shopify_agent,
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

    def _configure_budgets(self) -> None:
        self.budget.set_budget("daily", config.DAILY_BUDGET_LIMIT)
        self.budget.set_budget("shopify", config.SHOPIFY_BUDGET_LIMIT)
        self.budget.set_budget("ceo_llm", config.CEO_LLM_BUDGET_LIMIT)

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


_system: System | None = None


def get_system() -> System:
    global _system
    if _system is None:
        _system = System()
    return _system
