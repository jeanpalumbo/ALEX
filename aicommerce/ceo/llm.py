"""Thin wrapper around the Anthropic API for the AI CEO's reasoning.

No API key is ever hardcoded here — it is read from the environment
(`ANTHROPIC_API_KEY`, loaded from `.env` by `aicommerce.config`). If it is
missing, every call raises `LLMNotConfigured` with a message explaining
exactly what to set — callers must handle that explicitly rather than
silently falling back to a fabricated answer (Reality-First).
"""
from __future__ import annotations

import json
import threading
from datetime import date
from dataclasses import dataclass
from typing import Any, Optional

from aicommerce import config


class LLMNotConfigured(RuntimeError):
    pass


class OllamaLimitReached(LLMNotConfigured):
    """Daily Ollama call cap hit; FallbackModel treats it as 'try the next model'."""


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


class FallbackModel:
    """Tries each model in order, falling back to the next only when the
    current one is unconfigured or its call raises -- gives the free-tier
    background path real resilience (e.g. local Ollama down -> OpenRouter;
    OpenRouter rate-limited -> local Ollama) without the caller (ModelRouter/
    PersonaAgent) needing to know a fallback chain exists. `free` mirrors the
    first model that actually answers, so ModelRouter still records real $0
    cost for a free model that happened to be second in the chain.
    """

    def __init__(self, *models) -> None:
        if not models:
            raise ValueError("FallbackModel requires at least one model")
        self.models = models
        self.model = "/".join(getattr(m, "model", "unknown") for m in models)
        self.last_model: Optional[str] = None

    @property
    def configured(self) -> bool:
        return any(m.configured for m in self.models)

    def call(
        self,
        system: str,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        last_exc: Optional[Exception] = None
        for m in self.models:
            if not m.configured:
                continue
            try:
                response = m.call(system, messages, tools=tools, max_tokens=max_tokens)
            except LLMNotConfigured as exc:
                last_exc = exc
                continue
            except Exception as exc:  # noqa: BLE001 — try the next model, don't crash the caller
                last_exc = exc
                continue
            self.free = getattr(m, "free", False)
            self.last_model = getattr(m, "model", "unknown")
            return response
        raise LLMNotConfigured(
            f"No model in the fallback chain is configured or reachable. Last error: {last_exc}"
        )


class OllamaModel:
    """Ollama's OpenAI-compatible endpoint -- works against either LOCAL
    Ollama (default http://localhost:11434/v1, no account/API key, runs on
    Jean's own GPU, genuinely $0) or OLLAMA CLOUD (base_url
    https://ollama.com/v1 + a real OLLAMA_API_KEY, a paid subscription --
    see https://ollama.com/settings/keys). Which one is active is entirely
    determined by OLLAMA_BASE_URL/OLLAMA_API_KEY in .env; the code path is
    identical either way. Reuses the same Anthropic<->OpenAI converter
    functions as OpenRouterModel, so it's a real drop-in: same messages/tools
    in, same LLMResponse shape out.

    `free = True` always -- for local this is literally true ($0/call); for
    Cloud it reflects that Jean explicitly pre-paid a flat monthly
    subscription to fix a real latency problem (single-GPU request
    queuing), not a per-call spend he didn't approve. It is NOT free in the
    sense of "no money ever changes hands" once Cloud is configured --
    going over the plan's included credits does cost more. Document that
    distinction to Jean rather than letting the `free` flag imply otherwise.

    Requires Ollama installed and running locally (for the local case) with
    the configured model already pulled (`ollama pull <model>`) -- this code
    never installs Ollama, starts the service, pulls models, or signs Jean
    up for Ollama Cloud. He does the subscription himself; this code only
    consumes the API key once he provides it.
    """

    free = True

    def __init__(
        self, base_url: Optional[str] = None, model: Optional[str] = None, api_key: Optional[str] = None,
    ) -> None:
        self.base_url = base_url or config.OLLAMA_BASE_URL
        self.model = model or config.OLLAMA_MODEL
        self.api_key = api_key if api_key is not None else config.OLLAMA_API_KEY
        self._client = None
        self._calls_lock = threading.Lock()
        self._calls_day = date.today()
        self._calls_today = 0

    def _reserve_call(self) -> None:
        cap = config.OLLAMA_MAX_CALLS_PER_DAY
        if cap <= 0:
            return
        with self._calls_lock:
            today = date.today()
            if today != self._calls_day:
                self._calls_day, self._calls_today = today, 0
            if self._calls_today >= cap:
                raise OllamaLimitReached(f"Ollama daily call cap ({cap}) reached; falling back.")
            self._calls_today += 1

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.model)

    def _client_or_raise(self):
        if not self.configured:
            raise LLMNotConfigured(
                "OLLAMA_MODEL/OLLAMA_BASE_URL not set. Install Ollama, run "
                "`ollama pull <model>` for the model named in OLLAMA_MODEL, "
                "and make sure Ollama is running (see .env.example)."
            )
        if self._client is None:
            import openai

            # Local Ollama ignores the key entirely; Ollama Cloud requires
            # the real OLLAMA_API_KEY as a Bearer token -- the openai SDK
            # sends whatever api_key we pass as `Authorization: Bearer ...`.
            self._client = openai.OpenAI(
                base_url=self.base_url,
                api_key=self.api_key or "ollama",
                timeout=config.OLLAMA_TIMEOUT_SECONDS,
                max_retries=0,
            )
        return self._client

    def call(
        self,
        system: str,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        client = self._client_or_raise()
        self._reserve_call()
        oi_messages = [{"role": "system", "content": system}] + _anthropic_messages_to_openai(messages)
        kwargs: dict[str, Any] = dict(model=self.model, messages=oi_messages, max_tokens=max_tokens)
        if tools:
            kwargs["tools"] = _anthropic_tools_to_openai(tools)
        response = client.chat.completions.create(**kwargs)
        return _openai_response_to_llm_response(response)
