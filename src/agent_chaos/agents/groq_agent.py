"""Optional Groq tool-calling agent; importing this module makes no network calls."""

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from .base import AgentResult


class GroqAgent:
    def __init__(self, model: str | None = None) -> None:
        load_dotenv()
        key = os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL")
        if not key or not self.model:
            raise RuntimeError("Set GROQ_API_KEY and GROQ_MODEL in .env; see .env.example")
        self.client = OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1")

    def run(self, task, executor) -> AgentResult:
        tools = []
        for tool in executor.registry.all():
            schema = tool.input_model.model_json_schema()
            schema.pop("title", None)
            tools.append({"type": "function", "function": {
                "name": tool.name, "description": tool.description, "parameters": schema,
            }})
        messages = [
            {"role": "system", "content": "Solve the task using the provided tools. Return the final answer as a number."},
            {"role": "user", "content": task.prompt},
        ]
        calls = 0
        for _ in range(8):
            response = self.client.chat.completions.create(model=self.model, messages=messages, tools=tools, tool_choice="auto")
            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))
            if not message.tool_calls:
                try:
                    answer = float(message.content.strip())
                    return AgentResult(answer=answer, steps=calls, tool_calls=calls)
                except (AttributeError, TypeError, ValueError):
                    return AgentResult(status="error", error="Model did not return a numeric answer", steps=calls, tool_calls=calls)
            for call in message.tool_calls:
                calls += 1
                try:
                    args = json.loads(call.function.arguments)
                    result = executor.call(call.function.name, **args)
                    payload = result.value
                except Exception as exc:  # noqa: BLE001 - tool failures must become model-visible tool results
                    payload = {"error": f"{type(exc).__name__}: {exc}"}
                messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(payload, default=str)})
        return AgentResult(status="budget_exceeded", error="Groq tool-call step cap reached", steps=calls, tool_calls=calls)
