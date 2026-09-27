"""CEOService — the thing the web layer (and, later, the scheduler) talks to.

Ties together: CEOModel (LLM) + CEOTools (bridge to the real control plane) +
CEOState (observable status) + CompanyBrain (conversation history + audit
trail). Every user message goes through a real Anthropic tool-use loop; every
tool call the model makes runs against the live Orchestrator/registry/
permissions/budget/approvals/brain — nothing here is a second, separate chatbot.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from aicommerce.brain.models import Confidence, MemoryKind, MemoryRecord
from aicommerce.ceo.llm import CEOModel, LLMNotConfigured
from aicommerce.ceo.model_router import ModelRouter
from aicommerce.ceo.orchestrator import Orchestrator
from aicommerce.ceo.state import CEOState, CycleStage
from aicommerce.ceo.tools import TOOL_SCHEMAS, CEOTools
from aicommerce.control_plane.budget import BudgetExceededError

SYSTEM_PROMPT = """You are the AI CEO of an AI Commerce Operating System — a real, small \
ecommerce company whose owner is Jean. You are not a generic assistant: you operate this \
specific company through real tools (Company Brain, agent registry, budgets, approvals).

Reality-First / Evidence-First is your constitution:
- Never state something about the company (products, orders, budget, decisions, what an \
agent did) unless you got it from a tool call in this conversation or it was told to you \
directly by the human just now. If you don't know, call a tool or say UNKNOWN.
- When you state something about the company, prefix the key claim with FACT:, INFERENCE:, \
HYPOTHESIS:, or UNKNOWN: as appropriate. Do not skip this for company-state claims.
- You are bounded by permissions, budget, QA and human approval — you cannot bypass them, \
and you should not act as if you could. If `propose_action` comes back pending_approval, \
tell the human clearly that it is waiting for them, not that it is done.
- Prefer calling `get_company_state` and `query_memory` before answering questions about \
what is going on, rather than answering from memory of this conversation alone.
- You have direct inspection tools for every control-plane component: `get_preflight` (why \
something is degraded/blocked, not just that it is), `get_scheduler_status` (is the scheduler \
actually running, when did each job last fire), `get_recent_events` (the real-time EventBus \
audit stream). Use them instead of inferring from Company Brain alone when asked to inspect \
or audit the system, or when you'd otherwise have to say UNKNOWN about something one of these \
tools can answer directly.
- Use `record_memory` to save important decisions/inferences/hypotheses so future \
conversations (even after a restart) have them. Use `set_objective` when the human gives you \
a goal to work on.
- When asked for a status report, daily brief, end-of-day report, or executive summary, call \
`generate_status_report` first and build your narrative strictly from its output — never \
invent a task's completion status (COMPLETED/IN PROGRESS/etc.) for work that isn't tracked by \
a real system yet; report only what actually happened (executed/blocked actions, pending \
approvals, budget, decisions) for that period.
- Be concise. This is an operating console, not a general chat.
"""


class _LLMBudgetExhausted(RuntimeError):
    """Internal control-flow signal: the ceo_llm budget ran out mid-turn."""


@dataclass
class ChatTurn:
    role: str  # "user" | "assistant"
    content: str
    tool_activity: list[dict] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CEOService:
    def __init__(
        self,
        orchestrator: Orchestrator,
        model: Optional[CEOModel] = None,
        scheduler=None,
        preflight_provider=None,
    ) -> None:
        self.orchestrator = orchestrator
        self.state = CEOState()
        self.tools = CEOTools(orchestrator, self.state, scheduler=scheduler, preflight_provider=preflight_provider)
        self.model = model or CEOModel()
        # ModelRouter separates "which model, at what cost/latency" from this
        # class's own chat loop (master plan Milestone 4). Any duck-typed
        # fake with .configured/.call() works here too, same as before.
        self.router = ModelRouter(self.model, events=getattr(orchestrator, "events", None))
        self.history: list[ChatTurn] = []

    @property
    def llm_configured(self) -> bool:
        return self.model.configured

    def chat(self, user_message: str) -> ChatTurn:
        self.history.append(ChatTurn(role="user", content=user_message))

        if not self.model.configured:
            reply = ChatTurn(
                role="assistant",
                content=(
                    "UNKNOWN: my language model is not configured (ANTHROPIC_API_KEY missing). "
                    "I can't reason about your message, but the rest of the system (agents, "
                    "budget, approvals, memory) is live — check the dashboard panels directly, "
                    "or set ANTHROPIC_API_KEY in .env and restart."
                ),
            )
            self.history.append(reply)
            return reply

        self.state.set_stage(CycleStage.OBSERVE)
        messages = self._build_messages()
        correlation_id = str(uuid.uuid4())

        tool_activity: list[dict] = []
        final_text = ""
        try:
            for _ in range(6):  # bounded agentic loop — never spins forever
                self.state.set_stage(CycleStage.DECIDE)
                routed = self.router.call(
                    SYSTEM_PROMPT, messages, tools=TOOL_SCHEMAS, task="ceo_chat", correlation_id=correlation_id
                )
                self._spend_llm_budget(routed.estimated_cost)
                response = routed.response
                messages.append({"role": "assistant", "content": response.raw_content})

                if not response.tool_calls:
                    final_text = response.text
                    break

                self.state.set_stage(CycleStage.ACT)
                tool_results = []
                for call in response.tool_calls:
                    result = self.tools.dispatch(call.name, call.input)
                    tool_activity.append({"tool": call.name, "input": call.input, "result": result})
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": call.id,
                            "content": _stringify(result),
                        }
                    )
                messages.append({"role": "user", "content": tool_results})
            else:
                final_text = response.text or "(stopped after reaching the tool-call limit for this turn)"
        except LLMNotConfigured as exc:
            final_text = f"UNKNOWN: {exc}"
        except _LLMBudgetExhausted as exc:
            final_text = f"UNKNOWN: {exc} (this turn stopped early; whatever it already found is above.)"
        except Exception as exc:  # noqa: BLE001 — surface to the human, keep the console alive
            self.state.set_error(str(exc))
            final_text = f"UNKNOWN: the CEO hit an internal error talking to the model: {exc}"

        self.state.set_stage(CycleStage.LEARN)
        turn = ChatTurn(role="assistant", content=final_text, tool_activity=tool_activity)
        self.history.append(turn)

        self.orchestrator.brain.record(
            MemoryRecord(
                kind=MemoryKind.EPISODIC,
                content=f"CEO chat turn. User: {user_message!r}. CEO: {final_text!r}. Tools used: {[t['tool'] for t in tool_activity]}",
                source="ai_ceo",
                confidence=Confidence.FACT,
                tags=("chat",),
            )
        )
        self.state.set_stage(CycleStage.IDLE)
        return turn

    def _spend_llm_budget(self, cost: float) -> None:
        """Best-effort: enforce the `ceo_llm` budget if the deployment defined
        one. If it didn't (e.g. a lightweight test orchestrator), this is a
        no-op rather than an error — budget enforcement here is a policy
        choice, not a hard requirement for CEOService to function."""
        if cost <= 0:
            return
        try:
            self.orchestrator.budget.spend("ceo_llm", cost)
        except KeyError:
            pass
        except BudgetExceededError as exc:
            raise _LLMBudgetExhausted(str(exc)) from exc

    def _build_messages(self) -> list[dict]:
        # Keep the last N turns as plain text; tool_use/tool_result blocks from
        # earlier turns are not replayed (they were already folded into the
        # assistant's final text and into Company Brain).
        messages = []
        for turn in self.history[-20:]:
            if turn.role == "user":
                messages.append({"role": "user", "content": turn.content})
            elif turn.content:
                messages.append({"role": "assistant", "content": turn.content})
        return messages


def _stringify(value) -> str:
    import json

    try:
        return json.dumps(value)
    except TypeError:
        return str(value)
