"""Runs simulated tools through optional resilience stages."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from .clock import VirtualClock
from .errors import BudgetExceeded, CircuitOpen, RateLimited, ToolError, ValidationFailed
from .faults import FaultInjector
from .resilience import CircuitBreaker, ResilienceConfig, backoff_delay
from .tools import ToolRegistry


@dataclass
class Metrics:
    tool_calls: int = 0
    retries: int = 0
    extra_calls: int = 0
    validation_failures: int = 0
    breaker_trips: int = 0
    degraded_calls: int = 0


@dataclass
class CallResult:
    value: Any
    degraded: bool = False
    attempts: int = 1
    extra_calls: int = 0
    virtual_latency_s: float = 0.0


class ResilientExecutor:
    def __init__(self, registry: ToolRegistry | None = None, faults: FaultInjector | None = None,
                 clock: VirtualClock | None = None, config: ResilienceConfig | None = None, seed: int = 0) -> None:
        self.registry = registry or ToolRegistry()
        self.clock = clock or VirtualClock()
        self.faults = faults or FaultInjector(seed, clock=self.clock)
        self.config = config or ResilienceConfig.baseline()
        self.metrics = Metrics()
        self._breakers: dict[str, CircuitBreaker] = {}
        self._fallback: dict[str, Any] = {}
        self._calls_seen: set[tuple[str, tuple[tuple[str, str], ...]]] = set()
        self._steps = 0

    def _breaker(self, name: str) -> CircuitBreaker:
        return self._breakers.setdefault(name, CircuitBreaker(self.clock, self.config.failure_threshold,
                                                               self.config.recovery_timeout_s))

    def call(self, tool_name: str, **args: Any) -> CallResult:
        started = self.clock.now()
        self._steps += 1
        signature = (tool_name, tuple(sorted((key, repr(value)) for key, value in args.items())))
        if self.config.guards_enabled:
            if self._steps > self.config.max_steps or signature in self._calls_seen:
                raise BudgetExceeded("Agent step budget exceeded or repeated identical call detected")
            self._calls_seen.add(signature)
        tool = self.registry.get(tool_name)
        parsed = tool.input_model(**args)
        breaker = self._breaker(tool_name)
        if self.config.breaker_enabled:
            breaker.before_call()
        max_attempts = self.config.retry.max_attempts if self.config.retry_enabled else 1
        attempts = 0
        last_error: Exception | None = None
        try:
            while attempts < max_attempts:
                attempts += 1
                try:
                    value, calls = self._read(tool_name, tool, parsed.model_dump())
                    if self.config.validation_enabled:
                        try:
                            value = tool.output_model.model_validate(value).model_dump()
                        except (ValidationError, TypeError, ValueError) as exc:
                            self.metrics.validation_failures += 1
                            raise ValidationFailed(str(exc)) from exc
                    if self.config.invariants_enabled and tool.invariant and not tool.invariant(value):
                        raise ValidationFailed("Tool output violated plausibility invariant")
                    if self.config.breaker_enabled:
                        breaker.success()
                    self._fallback[tool_name] = value
                    extra = max(0, calls - 1) + max(0, attempts - 1)
                    self.metrics.extra_calls += extra
                    return CallResult(value, False, attempts, extra, self.clock.now() - started)
                except (ToolError, ValidationFailed) as exc:
                    last_error = exc
                    if attempts >= max_attempts or not self._retryable(exc):
                        # Count one failed logical call, not every failed attempt inside it.
                        if self.config.breaker_enabled:
                            breaker.failure()
                        raise
                    self.metrics.retries += 1
                    delay = backoff_delay(attempts - 1, self.config.retry,
                                           random.Random(self.faults.seed + attempts))
                    if isinstance(exc, RateLimited):
                        delay = max(delay, exc.retry_after)
                    self.clock.sleep(delay)
            raise last_error or RuntimeError("No tool attempts made")
        except (ToolError, ValidationFailed, TypeError, ValueError, KeyError):
            if self.config.fallback_enabled and tool_name in self._fallback:
                self.metrics.degraded_calls += 1
                return CallResult(self._fallback[tool_name], True, attempts, 0, self.clock.now() - started)
            raise
        finally:
            if self.config.breaker_enabled:
                self.metrics.breaker_trips = sum(item.trips for item in self._breakers.values())

    def _read(self, name: str, tool: Any, args: dict[str, Any]) -> tuple[Any, int]:
        reads = self.config.redundancy_reads if (self.config.redundancy_enabled and tool.read_only and name in self.config.redundancy_tools) else 1
        values = []
        for _ in range(reads):
            self.metrics.tool_calls += 1
            values.append(self.faults.apply(name, tool.fn(**args), self.config.timeout_s if self.config.timeout_enabled else None))
        if reads == 1 or all(value == values[0] for value in values):
            return values[0], reads
        self.metrics.tool_calls += 1
        third = self.faults.apply(name, tool.fn(**args), self.config.timeout_s if self.config.timeout_enabled else None)
        values.append(third)
        for value in values:
            if sum(candidate == value for candidate in values) >= 2:
                return value, 3
        raise ValidationFailed("Redundant tool reads did not agree")

    @staticmethod
    def _retryable(error: Exception) -> bool:
        return isinstance(error, (ToolError, ValidationFailed)) and not isinstance(error, CircuitOpen)

