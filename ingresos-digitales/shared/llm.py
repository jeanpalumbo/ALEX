"""Thin wrapper over the Anthropic SDK with retries and per-call cost logging.

Every script that uses it should call `LLM.print_cost_summary()` at the end
(rule 8 of the plan: paid scripts report calls and estimated cost).
"""

from __future__ import annotations

import sqlite3

from shared import db
from shared.config import get_settings

# USD per million tokens (input, output). Check current prices before relying on them.
PRICES_PER_MTOK = {
    "claude-opus-5-5": (4.00, 20.00),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-haiku-5-5": (0.10, 0.50),
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    price_in, price_out = PRICES_PER_MTOK.get(model, PRICES_PER_MTOK["claude-opus-5-5"])
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


class LLM:
    def __init__(self, model: str | None = None, conn: sqlite3.Connection | None = None,
                 max_retries: int = 4):
        import anthropic  # optional dependency: pip install .[llm]

        settings = get_settings()
        if not settings.has_llm:
            raise RuntimeError("ANTHROPIC_API_KEY is not set (see .env.example)")
        self.model = model or settings.llm_model
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key,
                                          max_retries=max_retries)
        self.conn = conn or db.connect()
        self.calls = 0
        self.cost_usd = 0.0

    def complete(self, prompt: str, system: str | None = None, max_tokens: int = 16000,
                 purpose: str = "") -> str:
        kwargs = {"system": system} if system else {}
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        usage = response.usage
        cost = estimate_cost(self.model, usage.input_tokens, usage.output_tokens)
        self.calls += 1
        self.cost_usd += cost
        self.conn.execute(
            "INSERT INTO llm_usage (model, purpose, input_tokens, output_tokens, cost_usd)"
            " VALUES (?, ?, ?, ?, ?)",
            (self.model, purpose, usage.input_tokens, usage.output_tokens, cost),
        )
        self.conn.commit()
        if response.stop_reason == "refusal":
            raise RuntimeError("model declined the request")
        return "".join(b.text for b in response.content if b.type == "text")

    def print_cost_summary(self) -> None:
        print(f"LLM calls: {self.calls} · estimated cost: ${self.cost_usd:.4f} ({self.model})")
