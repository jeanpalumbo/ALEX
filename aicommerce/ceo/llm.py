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
    input_tokens: int = 0
    output_tokens: int = 0


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

        usage = getattr(response, "usage", None)
        return LLMResponse(
            text="\n".join(text_parts),
            tool_calls=tool_calls,
            stop_reason=response.stop_reason,
            raw_content=[b.model_dump() for b in response.content],
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0,
        )


class OpenRouterModel:
    """Free-tier model for LOW-STAKES background use only (e.g. a persona's
    autonomous check-in), via OpenRouter's OpenAI-compatible API. No tool-use
    support -- it's plain text in, text out, which is all an autonomous
    check-in actually needs. Do not use this for the CEO's real interactive
    reasoning or anything Jean is actively relying on; it's a genuinely
    weaker model with real rate limits (OpenRouter's free tier: ~20 req/min,
    50-1000/day). `free = True` tells ModelRouter not to charge the normal
    Anthropic-pricing cost estimate against a call that actually cost $0.

    Requires Jean to create his own free OpenRouter account and API key --
    this code never does that for him.
    """

    free = True

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        self.api_key = api_key if api_key is not None else config.OPENROUTER_API_KEY
        self.model = model or config.OPENROUTER_MODEL
        self._client = None

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _client_or_raise(self):
        if not self.configured:
            raise LLMNotConfigured(
                "OPENROUTER_API_KEY is not set. Create a free account at openrouter.ai, get an "
                "API key, and add it to ai-commerce-os/.env (see .env.example) to enable "
                "free-tier background reasoning."
            )
        if self._client is None:
            import openai

            self._client = openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key)
        return self._client

    def call(
        self,
        system: str,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        if tools:
            raise NotImplementedError("OpenRouterModel does not support tool use — text-only background reasoning")

        client = self._client_or_raise()
        oi_messages = [{"role": "system", "content": system}]
        for m in messages:
            content = m["content"]
            if not isinstance(content, str):
                raise NotImplementedError(
                    "OpenRouterModel only supports plain-text messages, not tool_use/tool_result blocks"
                )
            oi_messages.append({"role": m["role"], "content": content})

        response = client.chat.completions.create(model=self.model, messages=oi_messages, max_tokens=max_tokens)
        choice = response.choices[0]
        text = choice.message.content or ""
        usage = getattr(response, "usage", None)
        return LLMResponse(
            text=text,
            tool_calls=[],
            stop_reason=choice.finish_reason or "stop",
            raw_content=[{"type": "text", "text": text}],
            input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
            output_tokens=getattr(usage, "completion_tokens", 0) or 0,
        )
