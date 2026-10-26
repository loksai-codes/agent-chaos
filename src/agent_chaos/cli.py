"""Command line interface for demos, experiments, and reports."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .experiments import load_config, run_experiment, write_results
from .faults import fault_descriptions
from .report import build_report, load_results

app = typer.Typer(help="Chaos testing for tool-using agents")
console = Console()
ROOT = Path(__file__).resolve().parents[2]


@app.command()
def demo() -> None:
    config = load_config(ROOT / "experiments" / "demo.yaml")
    rows = run_experiment(config)
    out = ROOT / "results" / "demo"
    write_results(rows, out, config)
    build_report({"seed": config.seed, "config": config.model_dump(), "rows": rows},
                 out / "report.md", out / "charts", rate=.2)
    table = Table(title="agent-chaos demo — scripted agent, simulated tools")
    for column in ("Fault", "Baseline success", "Resilient success", "Resilient silent failures"):
        table.add_column(column)
    for fault in config.faults:
        pair = []
        for condition in ("baseline", "resilient"):
            sample = [r for r in rows if r["fault"] == fault and r["condition"] == condition and r["rate"] == .2]
            pair.append(sample)
        success = lambda sample: f"{sum(r['outcome'] == 'correct' for r in sample) / len(sample):.1%}" if sample else "n/a"
        silent = lambda sample: f"{sum(r['outcome'] == 'wrong_silent' for r in sample) / len(sample):.1%}" if sample else "n/a"
        table.add_row(fault, success(pair[0]), success(pair[1]), silent(pair[1]))
    console.print(table)
    console.print(f"Report: {out / 'report.md'}")


@app.command()
def run(config: Annotated[Path, typer.Option("--config", exists=True)],
        out: Annotated[Path, typer.Option("--out")] = Path("results")) -> None:
    try:
        experiment = load_config(config)
        rows = run_experiment(experiment)
        write_results(rows, out, experiment)
        console.print(f"Wrote {len(rows)} runs to {out}")
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc


@app.command()
def report(results: Path, out: Annotated[Path, typer.Option("--out")] = Path("report.md"),
           charts_dir: Annotated[Path, typer.Option("--charts-dir")] = Path("charts"),
           rate: Annotated[float, typer.Option("--rate")] = .2) -> None:
    text = build_report(load_results(results), out, charts_dir, rate)
    console.print(f"Wrote report to {out} ({len(text)} characters)")


@app.command()
def faults() -> None:
    table = Table(title="Fault catalog")
    table.add_column("Fault")
    table.add_column("Behavior")
    for name, description in fault_descriptions():
        table.add_row(name, description)
    console.print(table)


if __name__ == "__main__":
    app()
