"""ModelRouter — separates "which model handles this call, and what did it
cost" from the CEO's own reasoning loop (master plan section 5.6 / Milestone
4: "Separar ModelRouter de la lógica del CEO").

There is exactly one approved provider/model configured in this environment
(Anthropic, `config.CEO_MODEL`) — this router does not invent a second
provider or a fallback chain that doesn't exist. What it does do, for real:
records provider/model/task/latency/tokens/cost/error/correlation id for
every call (to the EventBus, so it's durable and queryable), and gives future
routing rules (by task complexity/sensitivity/budget) exactly one place to
live instead of being scattered through CEOService.

If/when a second approved provider is configured, `route()` is the only
function that needs a routing rule added — callers don't change.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass
from typing import Optional

from aicommerce.ceo.llm import CEOModel, LLMNotConfigured, LLMResponse
from aicommerce.control_plane.events import EventBus

# Anthropic list pricing is not looked up dynamically here (no network call
# just to price a call) — this is a rough, documented estimate for budget
# tracking, not an invoice. Update if the configured model changes tier.
_ESTIMATED_COST_PER_1K_INPUT_TOKENS = 0.003
_ESTIMATED_COST_PER_1K_OUTPUT_TOKENS = 0.015


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1000 * _ESTIMATED_COST_PER_1K_INPUT_TOKENS
        + output_tokens / 1000 * _ESTIMATED_COST_PER_1K_OUTPUT_TOKENS
    )


@dataclass
class RoutedCall:
    response: LLMResponse
    model: str
    latency_ms: float
    estimated_cost: float
    correlation_id: str


class ModelRouter:
    def __init__(self, model: CEOModel, events: Optional[EventBus] = None) -> None:
        self.model = model
        self.events = events

    @property
    def configured(self) -> bool:
        return self.model.configured

    def call(
        self,
        system: str,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        max_tokens: int = 1024,
        task: str = "ceo_chat",
        correlation_id: Optional[str] = None,
    ) -> RoutedCall:
        correlation_id = correlation_id or str(uuid.uuid4())
        start = time.monotonic()
        try:
            response = self.model.call(system, messages, tools=tools, max_tokens=max_tokens)
        except LLMNotConfigured:
            raise
        except Exception as exc:
            latency_ms = (time.monotonic() - start) * 1000
            self._publish(
                "model.call_failed",
                {
                    "task": task,
                    "model": getattr(self.model, "model", "unknown"),
                    "latency_ms": round(latency_ms, 1),
                    "error": str(exc),
                    "correlation_id": correlation_id,
                },
            )
            raise

        latency_ms = (time.monotonic() - start) * 1000
        is_free = getattr(self.model, "free", False)
        cost = 0.0 if is_free else estimate_cost(response.input_tokens, response.output_tokens)
        self._publish(
            "model.call",
            {
                "task": task,
                "provider": "free" if is_free else "anthropic",
                "model": getattr(self.model, "model", "unknown"),
                "latency_ms": round(latency_ms, 1),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "estimated_cost": round(cost, 6),
                "stop_reason": response.stop_reason,
                "correlation_id": correlation_id,
            },
        )
        return RoutedCall(
            response=response,
            model=getattr(self.model, "model", "unknown"),
            latency_ms=latency_ms,
            estimated_cost=cost,
            correlation_id=correlation_id,
        )

    def _publish(self, event_type: str, payload: dict) -> None:
        if self.events is not None:
            self.events.publish(event_type, payload)
