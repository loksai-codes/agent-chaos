# 03: Scripted agent and Groq agent

**Read first:** PRD sections 5 (outcome classification), 6 (FR-6, FR-7) and 12.

## Task
1. `agents/base.py`: an `Agent` Protocol with `run(task, executor) -> AgentResult` where `AgentResult` has `answer`, `status` (`finished`, `error`, `budget_exceeded`), `error`, `steps`, `tool_calls`.
2. `agents/scripted.py`: runs a task's naive `solve(ctx)` where `ctx.call` goes through the executor. Catch tool-layer exceptions and naive-parsing errors (`KeyError`, `TypeError`, `ValueError`) and record them as `status="error"` with the message. Do not make the agent smarter; its fragility is what the experiment measures.
3. Add `classify_outcome(result, task)` returning `correct`, `wrong_silent`, `failed_loud` or `budget_exceeded` using the task's tolerance. An answer that is missing counts as `failed_loud`.
4. `agents/groq_agent.py`:
   - Use the `openai` SDK with `base_url="https://api.groq.com/openai/v1"`. Read `GROQ_API_KEY` and `GROQ_MODEL` from the environment (`.env` via python-dotenv). If missing, raise a friendly error pointing to `.env.example`.
   - Tool-calling loop (max 8 steps) over the same `ToolRegistry` through `ResilientExecutor`. Tool errors are returned to the model as tool messages so it can adapt. When baseline mode returns raw malformed output, pass it to the model as text.
   - Retry the LLM API itself on 429 and 5xx with exponential backoff, jitter and `Retry-After` (separate from tool resilience; pure delay function for testing). `--max-rpm` throttle, default 20.
   - Never log or store the key.

## Tests
- Scripted agent with no faults is correct on all tasks.
- With baseline config and `schema_drift` probability 1, the scripted agent ends as `failed_loud`; with `wrong_value` probability 1 it ends as `wrong_silent` (this demonstrates the silent-failure concept; assert it).
- `classify_outcome` for each of the four outcomes.
- Groq agent with a fake client: tool loop works, tool error is passed back, step cap yields `budget_exceeded`, backoff delays follow the schedule, key never appears in serialized output.

## Done when
`pytest` and `ruff check .` pass without a key. Commit, summarize, then wait for "next".
