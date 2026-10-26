"""Shared agent result types."""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class AgentResult:
    answer: Any = None
    status: str = "finished"
    error: str | None = None
    steps: int = 0
    tool_calls: int = 0


class Agent(Protocol):
    def run(self, task: Any, executor: Any) -> AgentResult: ...
