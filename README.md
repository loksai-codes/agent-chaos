# agent-chaos

Chaos testing and resilience experiments for tool-using AI agents. Break simulated tools on purpose, then measure whether retries, validation, redundancy, and fallbacks improve outcomes.

## Quickstart

Requires Python 3.11 or newer.

```powershell
python -m pip install -e ".[dev]"
chaos demo
```

The demo uses a scripted agent and simulated tools, so it needs no API key or network access. It writes CSV, JSON, a Markdown report, and charts under `results/demo/`.

## Commands

```text
chaos demo
chaos run --config experiments/default.yaml --out results/default
chaos report results/default/results.json --out results/default/report.md --charts-dir results/default/charts
chaos faults
```

An optional Groq agent can be configured with `GROQ_API_KEY` and `GROQ_MODEL` in a local `.env` file. Never commit that file. The key pasted into the project chat should be revoked and replaced before use.

## Scope

All tool data is deterministic and in memory. Faults include timeouts, transient errors, rate limits, malformed output, schema drift, empty output, wrong values, and latency spikes. Outcomes distinguish correct answers, silent wrong answers, loud failures, and budget exhaustion. See [PRD.md](PRD.md) for design and known limitations.

## Development

```powershell
python -m pytest
ruff check .
```

MIT licensed.
