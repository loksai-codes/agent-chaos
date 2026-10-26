# 01: Scaffold, world, tools, tasks and fault injectors

**Read first:** PRD sections 5, 6 (FR-1 to FR-3, FR-5), 10 and 12.

## Task
1. Initialize the project: `pyproject.toml` (package `agent_chaos` in `src/`, console script `chaos = agent_chaos.cli:app`), `.gitignore` (Python, `.env`, `results/`, caches), `.env.example` (`GROQ_API_KEY=`, `GROQ_MODEL=`), MIT `LICENSE`, placeholder `README.md`, ruff and pytest config.
2. `clock.py`: `VirtualClock` with `now()`, `sleep(seconds)` (advances time only), and `advance(seconds)`.
3. `errors.py`: `ToolError` base; `ToolTimeout`, `TransientError`, `RateLimited(retry_after)`, `ValidationFailed`, `CircuitOpen`, `BudgetExceeded`.
4. `world.py`: a deterministic world: exchange rates between at least 5 currencies (consistent, with a USD base), prices for about 8 items, distances between about 6 cities, fuel prices for about 5 countries. Use plain dictionaries with realistic fixed values. Provide `ground_truth` helpers.
5. `tools.py`: a `Tool` dataclass (`name`, `description`, `input_model`, `output_model`, `fn`, `read_only`, optional `invariant`), a `ToolRegistry`, and the five tools from PRD section 5. Invariants: rate in a bounded plausible range, prices and distances positive and under a ceiling.
6. `faults.py`:
   - `FaultConfig(fault, probability, tools=None, params={})`.
   - A `FaultInjector` that, for each call, derives a seeded RNG from `(seed, tool, call_index)` and decides whether to fire.
   - Implement all eight faults in PRD section 5. `timeout` and `latency_spike` use the virtual clock; `rate_limit` carries `retry_after`; `malformed_output` returns a truncated JSON string or a non-dict; `schema_drift` renames a key or changes a number to a string; `wrong_value` scales by 10x, 0.1x or swaps in a stale value while keeping the right type.
   - A `chaos faults` friendly description table (data only for now; the CLI comes later).
7. `tasks.py`: at least 8 tasks requiring 2 to 4 tool calls each, each with: id, natural-language prompt, a naive scripted `solve(ctx)` that calls `ctx.call(tool, **args)` and uses direct key access on results, a ground-truth answer from the world, and a tolerance.

## Tests
- Clock behavior, including that `sleep` never really sleeps.
- Determinism: same `(seed, tool, call_index)` always gives the same decision; probability 0 never fires; probability 1 always fires; the empirical rate at p=0.3 over 5000 calls is within 0.03.
- One test per fault showing the exact failure shape.
- Every task's naive solver, run with no faults, produces its ground-truth answer.

## Done when
`pytest` and `ruff check .` pass. Commit, summarize, then wait for "next".
