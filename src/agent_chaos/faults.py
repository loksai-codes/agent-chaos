"""Reproducible faults applied around simulated calls."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from typing import Any

from .clock import VirtualClock
from .errors import RateLimited, ToolTimeout, TransientError


@dataclass(frozen=True)
class FaultConfig:
    fault: str
    probability: float
    tools: list[str] | None = None
    params: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.fault not in FAULTS:
            raise ValueError(f"Unknown fault: {self.fault}")
        if not 0 <= self.probability <= 1:
            raise ValueError("probability must be between 0 and 1")


class FaultInjector:
    def __init__(self, seed: int, configs: list[FaultConfig] | None = None, clock: VirtualClock | None = None) -> None:
        self.seed = seed
        self.configs = configs or []
        self.clock = clock or VirtualClock()
        self._indices: dict[str, int] = {}

    @staticmethod
    def rng_for(seed: int, tool: str, call_index: int) -> random.Random:
        digest = hashlib.sha256(f"{seed}:{tool}:{call_index}".encode()).digest()
        return random.Random(int.from_bytes(digest[:8], "big"))

    def apply(self, tool: str, value: Any, timeout_s: float | None = None) -> Any:
        index = self._indices.get(tool, 0)
        self._indices[tool] = index + 1
        result = value
        for config in self.configs:
            if config.tools and tool not in config.tools:
                continue
            rng = self.rng_for(self.seed, tool, index)
            if rng.random() >= config.probability:
                continue
            result = self._inject(config, result, timeout_s)
        return result

    def _inject(self, config: FaultConfig, value: Any, timeout_s: float | None) -> Any:
        params = config.params
        if config.fault == "timeout":
            latency = float(params.get("latency_s", (timeout_s or 5) + 1))
            self.clock.advance(latency)
            if timeout_s is None or latency > timeout_s:
                raise ToolTimeout(f"Virtual call took {latency:g}s")
            return value
        if config.fault == "latency_spike":
            self.clock.advance(float(params.get("latency_s", 10)))
        elif config.fault == "transient_error":
            raise TransientError("Injected transient error")
        elif config.fault == "rate_limit":
            raise RateLimited(float(params.get("retry_after", 1)))
        elif config.fault == "malformed_output":
            return params.get("output", '{"broken":')
        elif config.fault == "schema_drift":
            if isinstance(value, dict) and value:
                output = dict(value)
                key = str(params.get("key", next(iter(output))))
                if key in output:
                    renamed = str(params.get("renamed_key", f"{key}_changed"))
                    output[renamed] = output.pop(key)
                return output
            return value
        elif config.fault == "empty_output":
            return params.get("output", {})
        elif config.fault == "wrong_value":
            return self._wrong_value(value, params)
        return value

    @staticmethod
    def _wrong_value(value: Any, params: dict[str, Any]) -> Any:
        if not isinstance(value, dict):
            return value
        output = dict(value)
        keys = [key for key, item in output.items() if isinstance(item, (int, float)) and not isinstance(item, bool)]
        if not keys:
            return output
        key = str(params.get("key", keys[-1]))
        if key not in keys:
            key = keys[-1]
        mode = params.get("mode", "scale_10")
        factor = {"scale_10": 10, "scale_0.1": 0.1}.get(mode)
        output[key] = output[key] * factor if factor is not None else output[key] * 10
        return output


FAULTS = {
    "timeout": "Virtual latency exceeds the call timeout; loud failure.",
    "transient_error": "Temporary backend error; loud failure.",
    "rate_limit": "Rate-limit error with retry delay; loud failure.",
    "malformed_output": "Truncated JSON or non-dict output; loud failure.",
    "schema_drift": "Renamed output field; loud when validated.",
    "empty_output": "Returns an empty or null output; loud failure.",
    "wrong_value": "Plausible but incorrect typed value; silent failure.",
    "latency_spike": "Adds virtual latency without changing the result.",
}


def fault_descriptions() -> list[tuple[str, str]]:
    return list(FAULTS.items())
