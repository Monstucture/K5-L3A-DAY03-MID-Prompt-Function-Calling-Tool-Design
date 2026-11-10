from __future__ import annotations

import json
import os
from typing import Any

from providers.base import ModelResponse, ToolCall


def coerce_args(args: dict[str, Any], tool_name: str, tools: list[dict[str, Any]] | None) -> dict[str, Any]:
    """Small models often send integers/booleans as strings ("10", "true"); convert them per the tool schema."""
    schema = next((t["function"] for t in tools or [] if t.get("function", {}).get("name") == tool_name), {})
    props = schema.get("parameters", {}).get("properties", {})
    fixed = dict(args)
    for key, value in args.items():
        kind = props.get(key, {}).get("type")
        if not isinstance(value, str):
            continue
        if kind == "integer" and value.strip().lstrip("-").isdigit():
            fixed[key] = int(value)
        elif kind == "boolean" and value.strip().lower() in ("true", "false"):
            fixed[key] = value.strip().lower() == "true"
    return fixed


class OpenAIProvider:
    """OpenAI Chat Completions provider with normalized tool_calls output."""

    def __init__(
        self,
        *,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: str | None = None,
        default_model: str = "gpt-4o-mini",
        api_key_default: str | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self.max_tokens = max_tokens
        self.api_key_env = api_key_env
        self.api_key_default = api_key_default
        self.base_url = base_url
        self.default_model = default_model

    def complete(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, Any]] | None = None,
        *,
        model: str | None = None,
        temperature: float = 0.0,
        tool_choice: Any | None = None,
    ) -> ModelResponse:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install live provider dependency first: pip install openai") from exc

        api_key = os.getenv(self.api_key_env) or self.api_key_default
        if not api_key:
            raise RuntimeError(f"Missing API key env var: {self.api_key_env}")

        client = OpenAI(api_key=api_key, base_url=self.base_url)
        kwargs: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
            "temperature": temperature,
        }
        if self.max_tokens:
            kwargs["max_tokens"] = self.max_tokens
        if tools:
            kwargs["tools"] = tools
        if tool_choice is not None:
            kwargs["tool_choice"] = tool_choice

        resp = client.chat.completions.create(**kwargs)
        msg = resp.choices[0].message
        calls: list[ToolCall] = []
        for call in msg.tool_calls or []:
            raw_args = call.function.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                # Small models often emit malformed JSON. Keep the call so eval grades it
                # as a wrong-argument failure instead of hiding it as provider_error.
                args = {"_invalid_json_arguments": raw_args}
            if not isinstance(args, dict):
                args = {"_invalid_json_arguments": raw_args}
            args = coerce_args(args, call.function.name, tools)
            calls.append(ToolCall(name=call.function.name, args=args))
        return ModelResponse(text=msg.content, tool_calls=calls, raw=resp)
