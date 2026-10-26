from agent_chaos.clock import VirtualClock


def test_virtual_clock_advances_without_waiting() -> None:
    clock = VirtualClock()
    clock.sleep(2.5)
    assert clock.now() == 2.5
    clock.advance(1)
    assert clock.now() == 3.5

