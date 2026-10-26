"""Configurable mitigation stages and a virtual-time circuit breaker."""

from __future__ import annotations

import random
from dataclasses import dataclass

from pydantic import BaseModel, Field

from .clock import VirtualClock
from .errors import CircuitOpen


class RetryPolicy(BaseModel):
    max_attempts: int = 4
    base_delay_s: float = 0.5
    factor: float = 2.0
    max_delay_s: float = 8.0
    jitter: bool = True


def backoff_delay(attempt: int, policy: RetryPolicy, rng: random.Random | None = None) -> float:
    delay = min(policy.base_delay_s * policy.factor**attempt, policy.max_delay_s)
    return rng.uniform(0, delay) if policy.jitter and rng else delay


class ResilienceConfig(BaseModel):
    retry_enabled: bool = False
    breaker_enabled: bool = False
    timeout_enabled: bool = False
    validation_enabled: bool = False
    invariants_enabled: bool = False
    redundancy_enabled: bool = False
    fallback_enabled: bool = False
    guards_enabled: bool = False
    retry: RetryPolicy = Field(default_factory=RetryPolicy)
    timeout_s: float = 5.0
    failure_threshold: int = 3
    recovery_timeout_s: float = 30.0
    redundancy_reads: int = 2
    redundancy_tools: list[str] = Field(default_factory=lambda: ["get_exchange_rate", "get_price", "get_distance_km", "get_fuel_price"])
    max_steps: int = 12

    @classmethod
    def baseline(cls) -> ResilienceConfig:
        return cls()

    @classmethod
    def resilient(cls) -> ResilienceConfig:
        return cls(retry_enabled=True, breaker_enabled=True, timeout_enabled=True,
                   validation_enabled=True, invariants_enabled=True, redundancy_enabled=True,
                   fallback_enabled=True, guards_enabled=True)

    @classmethod
    def ablation(cls, name: str) -> ResilienceConfig:
        fields = {"retry": "retry_enabled", "breaker": "breaker_enabled", "timeout": "timeout_enabled",
                  "validation": "validation_enabled", "invariants": "invariants_enabled",
                  "redundancy": "redundancy_enabled", "fallback": "fallback_enabled", "guards": "guards_enabled"}
        if name.startswith("no_"):
            stage = name[3:]
            config = cls.resilient()
            if stage not in fields:
                raise ValueError(f"Unknown mitigation: {stage}")
            setattr(config, fields[stage], False)
            return config
        config = cls.baseline()
        if name not in fields:
            raise ValueError(f"Unknown mitigation: {name}")
        setattr(config, fields[name], True)
        return config


@dataclass
class CircuitBreaker:
    clock: VirtualClock
    failure_threshold: int = 3
    recovery_timeout_s: float = 30.0
    failures: int = 0
    opened_at: float | None = None
    probe_in_flight: bool = False
    trips: int = 0

    def before_call(self) -> None:
        if self.opened_at is None:
            return
        if self.clock.now() - self.opened_at < self.recovery_timeout_s:
            raise CircuitOpen("Circuit is open")
        if self.probe_in_flight:
            raise CircuitOpen("Half-open probe already in flight")
        self.probe_in_flight = True

    def success(self) -> None:
        self.failures = 0
        self.opened_at = None
        self.probe_in_flight = False

    def failure(self) -> None:
        self.probe_in_flight = False
        self.failures += 1
        if self.opened_at is not None or self.failures >= self.failure_threshold:
            self.opened_at = self.clock.now()
            self.trips += 1
