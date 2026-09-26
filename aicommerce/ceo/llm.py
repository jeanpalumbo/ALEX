"""Thin wrapper around the Anthropic API for the AI CEO's reasoning.

No API key is ever hardcoded here — it is read from the environment
(`ANTHROPIC_API_KEY`, loaded from `.env` by `aicommerce.config`). If it is
missing, every call raises `LLMNotConfigured` with a message explaining
exactly what to set — callers must handle that explicitly rather than
silently falling back to a fabricated answer (Reality-First).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from aicommerce import config


class LLMNotConfigured(RuntimeError):
    pass


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict


@dataclass
class LLMResponse:
    text: str
    tool_calls: list[ToolCall]
    stop_reason: str
    raw_content: list  # for feeding back into the next turn as assistant content


class CEOModel:
    """Wraps one Anthropic chat-with-tools call. Stateless — the caller owns
    the message history."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key if api_key is not None else config.ANTHROPIC_API_KEY
        self.model = model or config.CEO_MODEL
        self._client = None

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _client_or_raise(self):
        if not self.configured:
            raise LLMNotConfigured(
                "ANTHROPIC_API_KEY is not set. Add it to ai-commerce-os/.env "
                "(see .env.example) to enable the AI CEO's language model."
            )
        if self._client is None:
            import anthropic

            self._client = anthropic.Anthropic(api_key=self.api_key)
        return self._client

    def call(
        self,
        system: str,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        client = self._client_or_raise()
        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        if tools:
            kwargs["tools"] = tools

        response = client.messages.create(**kwargs)

        text_parts = []
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append(ToolCall(id=block.id, name=block.name, input=block.input))

        return LLMResponse(
            text="\n".join(text_parts),
            tool_calls=tool_calls,
            stop_reason=response.stop_reason,
            raw_content=[b.model_dump() for b in response.content],
        )
