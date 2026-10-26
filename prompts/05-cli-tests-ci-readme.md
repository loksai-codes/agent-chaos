# 05: CLI, CI and README

**Read first:** PRD sections 9, 11, 12 and 13.

## Task
1. `cli.py` with Typer: `chaos demo`, `chaos run`, `chaos report`, `chaos faults`, as in PRD section 9. `demo` runs `experiments/demo.yaml` and prints a Rich headline table (fault, baseline success, resilient success, silent-failure rate) in under 60 seconds. Validation errors exit with code 2 and a clear message. `chaos run --agent groq` uses a reduced matrix by default and warns about rate limits.
2. `.github/workflows/ci.yml`: Python 3.11 and 3.12, install dev extras, `ruff check .`, `pytest`. No secrets needed.
3. CLI tests with Typer's `CliRunner` (demo output contains the headline table, bad config exits 2). Run coverage, list uncovered branches in `resilience.py`, `executor.py`, `faults.py`, and add tests for them.
4. Final `README.md`:
   - Logo (`assets/logo.svg`, I will add it), project name and one-line pitch
   - "Why": agents depend on tools, tools fail in messy ways, nobody measures it
   - Quickstart that really works: install, `chaos demo`, view the report
   - **What it breaks:** table of the eight faults, with loud vs silent
   - **What it fixes:** the resilience pipeline as a short diagram (ASCII or Mermaid)
   - **Results:** embed `degradation_curves.png`, the headline table and the ablation table from the real sample run, labeled *scripted agent, simulated tools*
   - **What didn't work:** an honest section on silent failures and `wrong_value`, written from the generated "What did not work" data and the actual numbers
   - Run with Groq (short, with the free-tier caveat; results go in a TODO table for me to fill in)
   - Design choices (virtual clock, seeded faults, ablations), limitations, project structure
   - License and contact placeholders
5. Check the PRD acceptance criteria one by one, with a pass or fail table and the command used for each.
6. Secrets scan: search the repo and git history for `gsk_`, `GROQ_API_KEY=` with a value, and `.env` files. Report the result.

## Done when
CI workflow is valid, all acceptance criteria pass, README renders cleanly, secrets scan is clean. Commit with `docs: final README and CI`, summarize, and list what I must do manually (add logo, set repo description and topics, run the Groq demo and fill in the results table).
