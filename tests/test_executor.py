import pytest

from agent_chaos.agents.scripted import ScriptedAgent, classify_outcome
from agent_chaos.clock import VirtualClock
from agent_chaos.errors import ToolTimeout
from agent_chaos.executor import ResilientExecutor
from agent_chaos.faults import FaultConfig, FaultInjector
from agent_chaos.resilience import ResilienceConfig
from agent_chaos.tasks import TASKS


def test_baseline_scripted_agent_survives_clean_world():
    for task in TASKS:
        result = ScriptedAgent().run(task, ResilientExecutor())
        assert classify_outcome(result, task) == "correct"


def test_validation_and_retry_recovers_schema_drift():
    injector = FaultInjector(1, [FaultConfig("schema_drift", .5)])
    executor = ResilientExecutor(faults=injector, config=ResilienceConfig.resilient())
    result = executor.call("get_price", item="laptop")
    assert result.value["price_usd"] == 1200


def test_redundancy_can_detect_wrong_values():
    # This seed faults only the second read, so the clean first and third form a majority.
    injector = FaultInjector(11, [FaultConfig("wrong_value", .5)])
    executor = ResilientExecutor(faults=injector, config=ResilienceConfig.resilient())
    result = executor.call("get_price", item="laptop")
    assert result.value["price_usd"] == 1200
    assert executor.metrics.tool_calls == 3


def test_timeout_fault_uses_virtual_time():
    clock = VirtualClock()
    injector = FaultInjector(2, [FaultConfig("timeout", 1)], clock)
    executor = ResilientExecutor(faults=injector, clock=clock, config=ResilienceConfig.baseline())
    with pytest.raises(ToolTimeout):
        executor.call("get_price", item="laptop")
    assert clock.now() > 5
