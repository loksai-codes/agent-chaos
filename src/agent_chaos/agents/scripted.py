"""Naive scripted solver: it intentionally trusts tool response shapes."""

from ..errors import BudgetExceeded
from .base import AgentResult


class _Context:
    def __init__(self, executor):
        self.executor = executor
        self.calls = 0

    def call(self, tool_name: str, **args):
        before = self.executor.metrics.tool_calls
        result = self.executor.call(tool_name, **args)
        self.calls += self.executor.metrics.tool_calls - before
        return result.value


class ScriptedAgent:
    def run(self, task, executor) -> AgentResult:
        context = _Context(executor)
        try:
            answer = task.solve(context)
            return AgentResult(answer=answer, steps=context.calls, tool_calls=context.calls)
        except BudgetExceeded as exc:
            return AgentResult(status="budget_exceeded", error=str(exc), steps=context.calls, tool_calls=context.calls)
        except Exception as exc:  # noqa: BLE001 - this naive agent records parsing and tool failures as outcomes
            return AgentResult(status="error", error=f"{type(exc).__name__}: {exc}", steps=context.calls, tool_calls=context.calls)


def classify_outcome(result: AgentResult, task) -> str:
    if result.status == "budget_exceeded":
        return "budget_exceeded"
    if result.status != "finished" or result.answer is None:
        return "failed_loud"
    try:
        correct = abs(float(result.answer) - task.answer) <= task.tolerance
    except (TypeError, ValueError):
        correct = False
    return "correct" if correct else "wrong_silent"
