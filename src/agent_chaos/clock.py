"""Deterministic virtual time for fault simulation."""

from dataclasses import dataclass


@dataclass
class VirtualClock:
    """A monotonic clock whose sleep operation advances instantly."""

    _time: float = 0.0

    def now(self) -> float:
        return self._time

    def sleep(self, seconds: float) -> None:
        self.advance(seconds)

    def advance(self, seconds: float) -> None:
        if seconds < 0:
            raise ValueError("Virtual time cannot move backwards")
        self._time += seconds
