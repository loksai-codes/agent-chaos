# 02: Resilience layer and executor

**Read first:** PRD sections 5 (resilience layer), 6 (FR-4), 7 (resilience config) and 12.

## Task
1. `resilience.py`:
   - `ResilienceConfig` (Pydantic) with an `enabled` flag and separate switches and parameters for: retry, breaker, timeout, validation, invariants, redundancy, fallback, and agent-level guards. Provide presets: `baseline()` (everything off), `resilient()` (everything on), and `ablation(name)` helpers that turn on or off exactly one stage.
   - `RetryPolicy`: exponential backoff with optional jitter and `max_delay`. A pure function `backoff_delay(attempt, policy, rng)` so the schedule is testable. Honor `RateLimited.retry_after` if larger. Retry only retryable errors (`ToolTimeout`, `TransientError`, `RateLimited`, `ValidationFailed`).
   - `CircuitBreaker` per tool using the virtual clock: closed, open after the failure threshold of consecutive failures, rejects with `CircuitOpen` while open, half-open after the recovery timeout allows exactly one probe; success closes, failure reopens. Count trips.
   - `Fallback`: per-tool last-known-good cache that, when used, marks the result `degraded=True`.
2. `executor.py`: `ResilientExecutor.call(tool_name, **args)` running the pipeline in the PRD order: breaker check, call through the fault injector with a timeout measured in virtual time, validate against the tool's `output_model`, check invariants, redundancy (two reads, third read for majority, fail loudly if all three differ), retry loop, fallback. Return a `CallResult` with `value`, `degraded`, `attempts`, `extra_calls`, `virtual_latency_s`, and record counters (retries, breaker trips, validation failures) in a `Metrics` object.
   - With `baseline()` config, the executor must behave like a plain call: no retry, no validation, raw tool output returned to the agent (so schema drift and malformed output break the naive agent, which is the point).
   - Also implement agent-level guards: max steps and repeated-identical-call detection raising `BudgetExceeded`.

## Tests
- Backoff delays with jitter off, base 0.5, factor 2, max 8: `0.5, 1, 2, 4, 8, 8`. `retry_after` overrides when larger.
- Breaker state machine exactly as in PRD section 12, driven by the virtual clock.
- Validation rejects schema drift and malformed output; a retry that gets a clean response returns the clean value.
- Redundancy: one `wrong_value` among two reads triggers a third read and majority wins; three different values raise a loud failure.
- Fallback returns the last good value flagged as degraded; baseline never uses fallback.
- Ablation presets toggle exactly one stage.

## Done when
`pytest` and `ruff check .` pass. Commit, summarize, then wait for "next".
