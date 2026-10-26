# 04: Experiment runner, stats and reports

**Read first:** PRD sections 5 (metrics), 6 (FR-8, FR-9), 7 and 8.

## Task
1. `stats.py`: Wilson 95% interval, success rate helpers, and a function to decide whether two intervals are non-overlapping.
2. `experiments.py`:
   - Load and validate the YAML experiment config (PRD section 7) with Pydantic and clear errors.
   - Expand the matrix `task x fault x fault_rate x condition x run`. For each cell build a fresh `VirtualClock`, `FaultInjector` and `ResilientExecutor` with seeds derived from `(seed, task, fault, rate, condition, run)` via `hashlib`.
   - Record one row per run: task, fault, rate, condition, run, outcome, tool_calls, retries, extra_calls, virtual_latency_s, breaker_trips, degraded, error.
   - Support conditions `baseline`, `resilient`, `ablation: retry_only`, `ablation: validation_only`, `ablation: no_redundancy`, and generic `ablation: <stage>` / `without: <stage>`.
   - A worker pool is optional; the scripted agent is fast. Output identical regardless of order. Progress bar with Rich.
   - Write CSV and JSON atomically. Include config and seed in the JSON.
3. Create `experiments/default.yaml` (as in the PRD) and `experiments/demo.yaml` (a reduced version that finishes in under 60 seconds: 3 faults including `schema_drift` and `wrong_value`, rates `[0.0, 0.2]`, 15 runs per cell).
4. `report.py`: build the Markdown report with the six sections in PRD section 8 and the three charts (`degradation_curves.png`, `outcomes_stacked.png`, `ablation_heatmap.png`). The "What did not work" section must be generated from data: list fault types where resilient is not significantly better than baseline, or silent failures remain above 5%.
5. Generate and commit sample outputs under `examples/` from `experiments/default.yaml` with the scripted agent (`sample_results.json`, `sample_report.md`, charts). If default takes longer than 5 minutes, reduce `runs_per_cell` and say so.

## Tests
- Determinism: same config and seed give identical rows; a different seed differs.
- Ablation conditions differ from `resilient` only in the toggled stage (assert on the resolved config).
- Report contains all six sections, every fault name, and all three charts exist and are non-empty.
- Baseline vs resilient on `timeout` at rate 0.2 shows the resilient success rate is higher (assert direction only, not exact numbers).

## Done when
`chaos`-level logic works through Python calls and tests pass. Commit, summarize with the actual headline numbers you observed (do not embellish), then wait for "next".
