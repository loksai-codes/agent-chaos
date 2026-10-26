# PRD: agent-chaos

**Status:** Ready to build · **Target:** one working day · **License:** MIT

## 1. Summary

`agent-chaos` is a Python toolkit that does two things to a tool-using AI agent. First, it **breaks the agent's tools on purpose** (timeouts, malformed output, wrong values, schema changes, rate limits). Second, it provides a **resilience layer** (retries, output validation, circuit breaker, fallback, redundancy) and measures, with numbers, how much each mitigation helps. It reports the one thing most agent demos never show: how often the agent fails *silently*, returning a confident wrong answer.

## 2. Problem

Agents depend on tools, and real tools fail in messy ways. Backend engineers use chaos testing to find out how systems behave when dependencies misbehave; agent builders rarely do. As a result, nobody knows whether a tool-using agent would survive a timeout, a changed API field or a stale value, and nobody knows which fixes actually work.

## 3. Goals and non-goals

**Goals**
- G1. Inject realistic, reproducible faults into any tool call.
- G2. Provide a configurable resilience layer where each mitigation can be toggled for ablation.
- G3. Measure outcomes across fault type, fault rate and condition (baseline vs resilient vs ablations).
- G4. Separate **loud failures** (agent errors out) from **silent failures** (agent returns a wrong answer) and report both.
- G5. Run with no API key (scripted agent, virtual clock) and optionally with a real LLM agent on Groq.
- G6. Produce an honest findings report, including where mitigations do *not* work.

**Non-goals**
- Not a full agent framework.
- No claim that the resilience layer solves wrong-value faults; the project must show how far it gets.
- No web UI, no database, no real network calls to tools (tools are simulated against a deterministic in-memory world).

## 4. Users and use cases

- *Agent builder:* "What happens to my agent if the exchange-rate API returns garbage 20% of the time?"
- *Reviewer / hiring manager:* reads the README to judge the author's reliability engineering instincts.
- *Learner:* uses it to see retries, validation and circuit breakers working on agents.

## 5. Core concepts

**World.** A deterministic in-memory data source behind the tools (exchange rates, prices, distances, a calculator). Ground truth comes from here.

**Tools (v1).** Each tool has a Pydantic input model, a Pydantic output model and a function.

| Tool | Input | Output |
|---|---|---|
| `get_exchange_rate` | `base`, `quote` | `{rate: float}` |
| `get_price` | `item` | `{item: str, price_usd: float}` |
| `get_distance_km` | `origin`, `destination` | `{km: float}` |
| `get_fuel_price` | `country` | `{usd_per_liter: float}` |
| `calculator` | `expression` | `{result: float}` |

**Faults.** Seeded, per-tool configurable, applied around a tool call.

| Fault | Behavior | Kind |
|---|---|---|
| `timeout` | virtual latency exceeds the call timeout; raises `ToolTimeout` | loud |
| `transient_error` | raises `TransientError` (HTTP 500 style) | loud |
| `rate_limit` | raises `RateLimited(retry_after=s)` | loud |
| `malformed_output` | returns invalid or truncated JSON string, or a non-dict | loud |
| `schema_drift` | valid dict with a renamed key or changed type (e.g. `rate` becomes `exchange_rate`, or number becomes string) | loud if validated, else crash in agent |
| `empty_output` | returns `None` or `{}` | loud |
| `wrong_value` | valid schema and type, plausible but wrong value (scaled by 10x, 0.1x, or stale) | **silent** |
| `latency_spike` | adds large virtual latency, no error | silent (affects cost) |

**Resilience layer.** Pipeline applied to every tool call, each stage toggleable:
1. *Circuit breaker:* closed, open, half-open (threshold 3 consecutive failures, 30 s virtual recovery, one probe in half-open).
2. *Timeout:* per-call limit on virtual time.
3. *Output validation:* validate against the tool's Pydantic output model.
4. *Invariants:* optional per-tool plausibility checks (e.g. rate within a bounded range, non-negative price).
5. *Redundancy:* for read-only idempotent tools, read twice and compare; on mismatch read a third time and take the majority.
6. *Retry:* exponential backoff with jitter on retryable errors; honors `retry_after`.
7. *Fallback:* per-tool fallback (last known good value, flagged as `degraded`).
8. *Agent-level guards:* max steps and repeated-identical-call detection.

**Outcome classification** for each run:
- `correct`: answer matches ground truth within tolerance
- `wrong_silent`: agent finished and returned a wrong answer
- `failed_loud`: agent raised an error or reported failure
- `budget_exceeded`: hit step, retry or time budget

Headline metrics: success rate (with Wilson 95% interval), **silent-failure rate**, mean extra tool calls (overhead), mean virtual latency, breaker trips, degraded-answer rate.

## 6. Functional requirements

- **FR-1 Tools and world (MUST).** The five tools above over a deterministic world; ground truth computable without faults.
- **FR-2 Virtual clock (MUST).** All sleeping, timeouts and breaker timing use a `VirtualClock`. No real `time.sleep` anywhere in library code.
- **FR-3 Fault injectors (MUST).** All eight faults, each unit tested, seeded per `(seed, tool, call_index)` so reproducible regardless of execution order. Config: fault name, probability, optional list of target tools, optional parameters.
- **FR-4 Resilience executor (MUST).** `ResilientExecutor` implementing the pipeline in section 5, driven by a `ResilienceConfig` with an on/off switch and parameters per stage. A `baseline` config disables everything.
- **FR-5 Tasks (MUST).** At least 8 tasks needing 2 to 4 tool calls each, e.g. "How much does 3 laptops cost in EUR?" (price x exchange rate x 3), "Fuel cost of a trip from A to B" (distance x fuel price x consumption). Each task has a naive scripted solver and a ground-truth answer.
- **FR-6 Scripted agent (MUST).** Solves tasks by calling tools through the executor and parsing results *naively* (direct key access, no defensive checks), so faults break it in realistic ways. This is the main experimental subject; it needs no key.
- **FR-7 Groq agent (SHOULD).** An LLM tool-calling agent over Groq's OpenAI-compatible API using the same executor. Tool errors are returned to the model as tool messages.
- **FR-8 Experiment runner (MUST).** Cartesian matrix of `task x fault x fault_rate x condition x run`, with seeds. Conditions: `baseline`, `resilient`, and ablations (each mitigation alone, and `resilient` minus each mitigation).
- **FR-9 Results and report (MUST).** CSV and JSON of all runs; Markdown report with tables and charts (section 8).
- **FR-10 CLI (MUST).** `chaos demo | run | report | faults`.

## 7. Experiment configuration (YAML)

```yaml
name: default
agent: scripted            # scripted | groq
seed: 42
runs_per_cell: 30
fault_rates: [0.0, 0.1, 0.2, 0.4]
faults: [timeout, transient_error, rate_limit, malformed_output,
         schema_drift, empty_output, wrong_value]
tasks: all
conditions:
  - baseline
  - resilient
  - ablation: retry_only
  - ablation: validation_only
  - ablation: no_redundancy
resilience:
  retry: { max_attempts: 4, base_delay_s: 0.5, factor: 2, max_delay_s: 8, jitter: true }
  breaker: { failure_threshold: 3, recovery_timeout_s: 30 }
  timeout_s: 5
  redundancy: { reads: 2, tools: [get_exchange_rate, get_price, get_distance_km, get_fuel_price] }
```

## 8. Reports

Markdown report sections:
1. Setup (seed, runs per cell, faults, rates, conditions)
2. **Headline table:** for each fault at a fixed rate (default 0.2), success rate and silent-failure rate for baseline vs resilient, with Wilson intervals and the absolute improvement
3. **Ablation table:** which mitigation recovers which fault type
4. **Overhead:** mean extra tool calls and virtual latency per condition
5. **What did not work:** auto-generated list of fault types where the resilient condition is not significantly better than baseline, or where silent failures remain above 5%
6. Charts

Charts (Matplotlib, `Agg` backend):
- `degradation_curves.png`: success rate vs fault rate, one panel per fault type, lines for each condition
- `outcomes_stacked.png`: stacked bars of `correct / wrong_silent / failed_loud / budget_exceeded` for baseline vs resilient at the fixed rate
- `ablation_heatmap.png`: fault types x mitigations, color is success-rate gain

## 9. CLI

```
chaos demo                                  # small fast experiment, prints headline table
chaos run --config experiments/default.yaml [--out results/] [--agent scripted|groq]
chaos report RESULTS.json [--out report.md] [--charts-dir charts/] [--rate 0.2]
chaos faults                                # lists faults and what each does
```

## 10. Architecture and repo layout

```
agent-chaos/
  README.md  PRD.md  LICENSE  pyproject.toml  .gitignore  .env.example
  src/agent_chaos/
    __init__.py  clock.py  errors.py  world.py  tools.py  tasks.py
    faults.py  resilience.py  executor.py
    agents/  base.py  scripted.py  groq_agent.py
    experiments.py  stats.py  report.py  cli.py
  experiments/  default.yaml  demo.yaml
  tests/        test_clock.py test_faults.py test_resilience.py test_breaker.py
                test_tasks.py test_experiments.py test_report.py test_groq_agent.py test_cli.py
  examples/     sample_results.json  sample_report.md  charts/
  prompts/  assets/logo.svg  .github/workflows/ci.yml
```

Stack: Python 3.11+, Pydantic v2, Typer, Rich, PyYAML, Matplotlib, openai SDK, python-dotenv, pytest, ruff.

## 11. Non-functional requirements

- Deterministic for a given config and seed.
- `chaos demo` finishes in under 60 seconds; the default experiment in under 5 minutes on a laptop with the scripted agent.
- No real sleeping or network access in library code or tests.
- Type hints throughout; `ruff` clean.
- No secrets in repo, logs or results.

## 12. Testing strategy and vectors

- **Backoff schedule** with jitter off, base 0.5, factor 2, max 8: delays `0.5, 1, 2, 4, 8, 8`.
- **Circuit breaker:** closed, then open after 3 consecutive failures; calls rejected with `CircuitOpen` while open; after 30 virtual seconds the next call is a half-open probe; probe success closes, probe failure reopens.
- **Fault determinism:** the same `(seed, tool, call_index)` always produces the same fault decision; probability 0 never fires; probability 1 always fires; empirical firing rate at p=0.3 over 5000 calls within 0.03.
- **Each fault:** a unit test showing the exact failure shape (exception type, malformed string, renamed key, scaled value).
- **Validation:** schema drift and malformed output are rejected by the validator and retried; a retry that succeeds returns the clean value.
- **Redundancy:** two reads disagree (wrong_value on one) triggers a third read and majority wins; if all three disagree the call fails loudly instead of returning a guess.
- **Experiment:** same seed gives identical results; ablation conditions differ from `resilient` only in the toggled stage.
- **Groq agent:** fake client, tool error passed back to the model, step cap, no network.

## 13. Acceptance criteria

1. `chaos demo` runs with no key and prints a headline table.
2. For loud faults (`timeout`, `transient_error`, `rate_limit`, `malformed_output`, `schema_drift`, `empty_output`) at rate 0.2, the resilient condition beats baseline with non-overlapping 95% intervals in the sample report.
3. The report shows silent-failure rate separately for `wrong_value`, and states honestly how much redundancy and invariants recover.
4. Ablation table and all three charts are generated.
5. `pytest` and `ruff check` pass; CI is green.
6. README embeds real sample outputs labeled "scripted agent, simulated tools". Groq results are added only after the owner runs them.

## 14. Milestones (one day)

| Block | Work |
|---|---|
| 1 hr | Scaffold, clock, errors, world, tools, tasks, fault injectors, tests |
| 1.5 hr | Resilience layer, breaker, executor, tests |
| 45 min | Scripted agent, experiment runner, stats |
| 45 min | Reports, charts, CLI |
| 30 min | Groq agent, CI, README, sample outputs |

## 15. Risks

- Wrong-value faults cannot be detected by retries. *Mitigation:* implement invariants and redundancy, measure them, and report honestly when silent failures remain.
- LLM agents on Groq may behave differently from the scripted agent. *Mitigation:* the Groq run uses a reduced matrix and its results are reported separately.
- Free-tier rate limits. *Mitigation:* small matrix, `--max-rpm`, resume.
