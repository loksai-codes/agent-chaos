import pytest

from agent_chaos.clock import VirtualClock
from agent_chaos.errors import RateLimited, ToolTimeout, TransientError
from agent_chaos.faults import FaultConfig, FaultInjector


def injector(fault: str, params: dict | None = None, seed: int = 17, clock: VirtualClock | None = None) -> FaultInjector:
    return FaultInjector(seed, [FaultConfig(fault, 1, params=params or {})], clock)


def test_fault_decision_is_seeded_by_tool_and_call_index() -> None:
    a = FaultInjector.rng_for(4, "get_price", 2).random()
    assert a == FaultInjector.rng_for(4, "get_price", 2).random()


def test_probability_zero_never_fires_and_one_always_fires() -> None:
    original = {"price_usd": 2.0}
    assert FaultInjector(5, [FaultConfig("wrong_value", 0)]).apply("get_price", original) == original
    assert FaultInjector(5, [FaultConfig("wrong_value", 1)]).apply("get_price", original) != original


def test_empirical_probability_is_close_to_configured_rate() -> None:
    count = sum(FaultInjector.rng_for(42, "tool", i).random() < .3 for i in range(5000))
    assert abs(count / 5000 - .3) < .03


def test_timeout_advances_virtual_clock_and_raises() -> None:
    clock = VirtualClock()
    with pytest.raises(ToolTimeout):
        injector("timeout", {"latency_s": 6}, clock=clock).apply("tool", {}, timeout_s=5)
    assert clock.now() == 6


def test_transient_error_shape() -> None:
    with pytest.raises(TransientError, match="Injected transient"):
        injector("transient_error").apply("tool", {})


def test_rate_limit_shape() -> None:
    with pytest.raises(RateLimited) as error:
        injector("rate_limit", {"retry_after": 3}).apply("tool", {})
    assert error.value.retry_after == 3


def test_malformed_output_shape() -> None:
    assert injector("malformed_output").apply("tool", {"x": 1}) == '{"broken":'


def test_schema_drift_renames_field() -> None:
    assert injector("schema_drift").apply("tool", {"rate": 1.2}) == {"rate_changed": 1.2}


def test_empty_output_shape() -> None:
    assert injector("empty_output").apply("tool", {"x": 1}) == {}


def test_wrong_value_keeps_type_and_scales() -> None:
    value = injector("wrong_value", {"mode": "scale_10"}).apply("tool", {"price_usd": 5.0})
    assert value == {"price_usd": 50.0}
    assert isinstance(value["price_usd"], float)


def test_latency_spike_advances_clock_and_preserves_value() -> None:
    clock = VirtualClock()
    value = injector("latency_spike", {"latency_s": 8}, clock=clock).apply("tool", {"ok": True})
    assert value == {"ok": True}
    assert clock.now() == 8
