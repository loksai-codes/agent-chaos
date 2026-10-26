from agent_chaos.faults import FaultInjector
from agent_chaos.tasks import TASKS
from agent_chaos.tools import ToolRegistry


class Context:
    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self.faults = FaultInjector(1)

    def call(self, tool_name: str, **args):
        tool = self.registry.get(tool_name)
        parsed = tool.input_model(**args)
        return self.faults.apply(tool_name, tool.fn(**parsed.model_dump()))


def test_every_task_matches_independent_ground_truth() -> None:
    for task in TASKS:
        assert abs(task.solve(Context()) - task.answer) <= task.tolerance
