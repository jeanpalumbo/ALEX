"""Tests for the Anthropic<->OpenAI message/tool conversion that lets
OpenRouterModel be a real drop-in for CEOModel -- same messages/tools in,
same LLMResponse shape out. No real network calls here (mocked client);
the live tool-calling capability itself was verified manually against the
real OpenRouter API on 2026-10-04."""
import json
from unittest.mock import MagicMock, patch

from aicommerce.ceo.llm import (
    OpenRouterModel,
    ToolCall,
    _anthropic_messages_to_openai,
    _anthropic_tools_to_openai,
    _openai_response_to_llm_response,
)


def test_anthropic_tools_convert_to_openai_function_schema():
    anthropic_tools = [
        {"name": "get_weather", "description": "get it", "input_schema": {"type": "object", "properties": {}}},
    ]
    openai_tools = _anthropic_tools_to_openai(anthropic_tools)
    assert openai_tools == [
        {
            "type": "function",
            "function": {"name": "get_weather", "description": "get it", "parameters": {"type": "object", "properties": {}}},
        }
    ]


def test_plain_string_messages_pass_through_unchanged():
    messages = [{"role": "user", "content": "hi"}]
    assert _anthropic_messages_to_openai(messages) == [{"role": "user", "content": "hi"}]


def test_assistant_tool_use_block_converts_to_openai_tool_calls():
    messages = [
        {
            "role": "assistant",
            "content": [{"type": "tool_use", "id": "call_1", "name": "get_weather", "input": {"city": "Madrid"}}],
        }
    ]
    converted = _anthropic_messages_to_openai(messages)
    assert converted[0]["role"] == "assistant"
    assert converted[0]["content"] is None
    assert converted[0]["tool_calls"][0]["id"] == "call_1"
    assert json.loads(converted[0]["tool_calls"][0]["function"]["arguments"]) == {"city": "Madrid"}


def test_user_tool_result_block_converts_to_openai_tool_message():
    messages = [
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "call_1", "content": "sunny"}]},
    ]
    converted = _anthropic_messages_to_openai(messages)
    assert converted[0] == {"role": "tool", "tool_call_id": "call_1", "content": "sunny"}


def test_multiple_tool_results_in_one_turn_become_separate_tool_messages():
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "tool_result", "tool_use_id": "a", "content": "1"},
                {"type": "tool_result", "tool_use_id": "b", "content": "2"},
            ],
        }
    ]
    converted = _anthropic_messages_to_openai(messages)
    assert len(converted) == 2
    assert converted[0]["tool_call_id"] == "a"
    assert converted[1]["tool_call_id"] == "b"


def test_openai_response_with_tool_calls_parses_into_llm_response():
    fake_tc = MagicMock()
    fake_tc.id = "call_9"
    fake_tc.function.name = "do_thing"
    fake_tc.function.arguments = '{"x": 1}'
    fake_choice = MagicMock(finish_reason="tool_calls")
    fake_choice.message.content = None
    fake_choice.message.tool_calls = [fake_tc]
    fake_response = MagicMock(choices=[fake_choice], usage=MagicMock(prompt_tokens=10, completion_tokens=5))

    result = _openai_response_to_llm_response(fake_response)

    assert result.tool_calls == [ToolCall(id="call_9", name="do_thing", input={"x": 1})]
    assert result.raw_content == [{"type": "tool_use", "id": "call_9", "name": "do_thing", "input": {"x": 1}}]
    assert result.input_tokens == 10
    assert result.output_tokens == 5


def test_openai_response_with_plain_text_parses_into_llm_response():
    fake_choice = MagicMock(finish_reason="stop")
    fake_choice.message.content = "hello"
    fake_choice.message.tool_calls = None
    fake_response = MagicMock(choices=[fake_choice], usage=None)

    result = _openai_response_to_llm_response(fake_response)

    assert result.text == "hello"
    assert result.tool_calls == []
    assert result.raw_content == [{"type": "text", "text": "hello"}]


def test_openrouter_model_call_with_tools_hits_the_real_client_shape():
    model = OpenRouterModel(api_key="fake-key", model="qwen/qwen3.8-27b:free")
    fake_choice = MagicMock(finish_reason="stop")
    fake_choice.message.content = "ok"
    fake_choice.message.tool_calls = None
    fake_response = MagicMock(choices=[fake_choice], usage=None)

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_response
    with patch("openai.OpenAI", return_value=fake_client):
        result = model.call(
            "system prompt",
            [{"role": "user", "content": "hi"}],
            tools=[{"name": "t", "description": "d", "input_schema": {}}],
        )

    assert result.text == "ok"
    call_kwargs = fake_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["tools"][0]["function"]["name"] == "t"
    assert call_kwargs["messages"][0] == {"role": "system", "content": "system prompt"}


def test_openrouter_model_without_tools_omits_tools_kwarg():
    model = OpenRouterModel(api_key="fake-key")
    fake_choice = MagicMock(finish_reason="stop")
    fake_choice.message.content = "ok"
    fake_choice.message.tool_calls = None
    fake_response = MagicMock(choices=[fake_choice], usage=None)

    fake_client = MagicMock()
    fake_client.chat.completions.create.return_value = fake_response
    with patch("openai.OpenAI", return_value=fake_client):
        model.call("sys", [{"role": "user", "content": "hi"}])

    assert "tools" not in fake_client.chat.completions.create.call_args.kwargs
