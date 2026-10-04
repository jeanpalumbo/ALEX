"""Thin wrapper around the Anthropic API for the AI CEO's reasoning.

No API key is ever hardcoded here — it is read from the environment
(`ANTHROPIC_API_KEY`, loaded from `.env` by `aicommerce.config`). If it is
missing, every call raises `LLMNotConfigured` with a message explaining
exactly what to set — callers must handle that explicitly rather than
silently falling back to a fabricated answer (Reality-First).
"""
from __future__ import annotations

import json
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
        max_tokens: int = 4096,
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


def _anthropic_tools_to_openai(tools: list[dict]) -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": t["name"],
                "description": t.get("description", ""),
                "parameters": t.get("input_schema", {"type": "object", "properties": {}}),
            },
        }
        for t in tools
    ]


def _anthropic_messages_to_openai(messages: list[dict]) -> list[dict]:
    """Converts our internal Anthropic-block-shaped message history into
    OpenAI's format, so any model exposed via an OpenAI-compatible API
    (OpenRouter, Ollama, ...) can be a real drop-in for CEOModel -- same
    `messages`/`tools` in, same `LLMResponse` shape out, so CEOService's
    chat loop and PersonaAgent don't need to know which provider is live."""
    out: list[dict] = []
    for m in messages:
        content = m["content"]
        if isinstance(content, str):
            out.append({"role": m["role"], "content": content})
            continue
        # content is a list of Anthropic content blocks
        if m["role"] == "assistant":
            text_parts = [b["text"] for b in content if b.get("type") == "text"]
            tool_use_blocks = [b for b in content if b.get("type") == "tool_use"]
            msg: dict = {"role": "assistant", "content": "\n".join(text_parts) or None}
            if tool_use_blocks:
                msg["tool_calls"] = [
                    {
                        "id": b["id"],
                        "type": "function",
                        "function": {"name": b["name"], "arguments": json.dumps(b["input"])},
                    }
                    for b in tool_use_blocks
                ]
            out.append(msg)
        else:  # user turn carrying tool_result blocks -> one "tool" message each
            for b in content:
                if b.get("type") == "tool_result":
                    out.append({"role": "tool", "tool_call_id": b["tool_use_id"], "content": b.get("content", "")})
                else:
                    out.append({"role": "user", "content": b.get("text", str(b))})
    return out


def _openai_response_to_llm_response(response) -> LLMResponse:
    choice = response.choices[0]
    message = choice.message
    text = message.content or ""
    tool_calls = []
    raw_content: list = []
    if text:
        raw_content.append({"type": "text", "text": text})
    for tc in message.tool_calls or []:
        try:
            arguments = json.loads(tc.function.arguments)
        except (json.JSONDecodeError, TypeError):
            arguments = {}
        tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, input=arguments))
        raw_content.append({"type": "tool_use", "id": tc.id, "name": tc.function.name, "input": arguments})

    usage = getattr(response, "usage", None)
    return LLMResponse(
        text=text,
        tool_calls=tool_calls,
        stop_reason=choice.finish_reason or "stop",
        raw_content=raw_content,
        input_tokens=getattr(usage, "prompt_tokens", 0) or 0,
        output_tokens=getattr(usage, "completion_tokens", 0) or 0,
    )


class OpenRouterModel:
    """Free-tier model, via OpenRouter's OpenAI-compatible API, with REAL
    tool-use support -- verified live on 2026-10-04 that several free
    models (qwen/qwen3.8-27b:free, nvidia/nemotron-3.5-lightning:free)
    correctly return real OpenAI-style tool_calls. This makes it a genuine
    drop-in for CEOModel: same messages/tools in, same LLMResponse shape
    out (see `_anthropic_messages_to_openai`/`_openai_response_to_llm_response`).

    Still a materially weaker model than Claude, and has real shared-pool
    rate limits (OpenRouter's free tier: ~20 req/min, 50-1000/day) -- the
    `openrouter/free` auto-router alias was found to be unreliable (it
    once routed a request to a content-safety classifier instead of a chat
    model), so `config.OPENROUTER_MODEL` defaults to a specific verified
    model id, not the alias. `free = True` tells ModelRouter to record the
    real cost ($0) instead of Anthropic pricing.

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
                "API key, and add it to ai-commerce-os/.env (see .env.example) to enable the "
                "free-tier model."
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
        max_tokens: int = 4096,
    ) -> LLMResponse:
        client = self._client_or_raise()
        oi_messages = [{"role": "system", "content": system}] + _anthropic_messages_to_openai(messages)
        kwargs: dict[str, Any] = dict(model=self.model, messages=oi_messages, max_tokens=max_tokens)
        if tools:
            kwargs["tools"] = _anthropic_tools_to_openai(tools)
        response = client.chat.completions.create(**kwargs)
        return _openai_response_to_llm_response(response)
