"""Deterministic experiment matrix and result serialization."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from .agents.groq_agent import GroqAgent
from .agents.scripted import ScriptedAgent, classify_outcome
from .clock import VirtualClock
from .executor import ResilientExecutor
from .faults import FaultConfig, FaultInjector
from .resilience import ResilienceConfig, RetryPolicy
from .tasks import TASKS


class ExperimentConfig(BaseModel):
    name: str = "demo"
    agent: str = "scripted"
    seed: int = 42
    runs_per_cell: int = 10
    fault_rates: list[float] = Field(default_factory=lambda: [0.0, 0.2])
    faults: list[str] = Field(default_factory=lambda: ["timeout", "schema_drift", "wrong_value"])
    tasks: list[str] | str = "all"
    conditions: list[str] = Field(default_factory=lambda: ["baseline", "resilient"])
    resilience: dict[str, Any] = Field(default_factory=dict)


def load_config(path: str | Path) -> ExperimentConfig:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        return ExperimentConfig.model_validate(raw)
    except Exception as exc:
        raise ValueError(f"Invalid experiment config {path}: {exc}") from exc


def _seed(*parts: object) -> int:
    digest = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return int.from_bytes(digest[:8], "big")


def _condition(name: str) -> ResilienceConfig:
    if name == "baseline":
        return ResilienceConfig.baseline()
    if name == "resilient":
        return ResilienceConfig.resilient()
    if name.startswith("ablation: "):
        return ResilienceConfig.ablation(name.split(":", 1)[1].strip())
    if name.startswith("without: "):
        return ResilienceConfig.ablation("no_" + name.split(":", 1)[1].strip())
    raise ValueError(f"Unknown experiment condition: {name}")


def run_experiment(config: ExperimentConfig) -> list[dict[str, Any]]:
    task_list = TASKS if config.tasks == "all" else [task for task in TASKS if task.id in config.tasks]
    agent = ScriptedAgent() if config.agent == "scripted" else GroqAgent()
    rows: list[dict[str, Any]] = []
    for task in task_list:
        for fault in config.faults:
            for rate in config.fault_rates:
                for condition in config.conditions:
                    for run in range(config.runs_per_cell):
                        seed = _seed(config.seed, task.id, fault, rate, condition, run)
                        clock = VirtualClock()
                        injector = FaultInjector(seed, [FaultConfig(fault, rate)], clock)
                        resilience = _condition(condition)
                        if config.resilience.get("retry"):
                            resilience.retry = RetryPolicy(**config.resilience["retry"])
                        executor = ResilientExecutor(faults=injector, clock=clock, config=resilience, seed=seed)
                        result = agent.run(task, executor)
                        metrics = executor.metrics
                        rows.append({"task": task.id, "fault": fault, "rate": rate, "condition": condition,
                                     "run": run, "outcome": classify_outcome(result, task),
                                     "tool_calls": metrics.tool_calls, "retries": metrics.retries,
                                     "extra_calls": metrics.extra_calls, "virtual_latency_s": clock.now(),
                                     "breaker_trips": metrics.breaker_trips,
                                     "degraded": metrics.degraded_calls > 0, "error": result.error})
    return rows


def write_results(rows: list[dict[str, Any]], out_dir: str | Path, config: ExperimentConfig) -> None:
    directory = Path(out_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_tmp = directory / "results.json.tmp"
    json_tmp.write_text(json.dumps({"config": config.model_dump(), "seed": config.seed, "rows": rows}, indent=2), encoding="utf-8")
    json_tmp.replace(directory / "results.json")
    csv_tmp = directory / "results.csv.tmp"
    with csv_tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    csv_tmp.replace(directory / "results.csv")
