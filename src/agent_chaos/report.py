"""Markdown summaries and charts from recorded run rows."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .stats import wilson_interval


def load_results(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_report(data: dict[str, Any], out_path: str | Path, charts_dir: str | Path, rate: float = 0.2) -> str:
    rows = data["rows"]
    charts = Path(charts_dir)
    charts.mkdir(parents=True, exist_ok=True)
    faults = sorted({row["fault"] for row in rows})
    conditions = sorted({row["condition"] for row in rows})

    def group(fault: str, condition: str, selected_rate: float = rate) -> list[dict[str, Any]]:
        return [row for row in rows if row["fault"] == fault and row["condition"] == condition and row["rate"] == selected_rate]

    lines = ["# agent-chaos experiment report", "", "## Setup", "",
             f"Seed: {data.get('seed', 'unknown')}; recorded runs: {len(rows)}.", "",
             "## Headline results", "", "| Fault | Condition | Success (95% Wilson CI) | Silent failure |", "|---|---|---:|---:|"]
    for fault in faults:
        for condition in ["baseline", "resilient"]:
            sample = group(fault, condition)
            if not sample:
                continue
            correct = sum(row["outcome"] == "correct" for row in sample)
            silent = sum(row["outcome"] == "wrong_silent" for row in sample)
            lo, hi = wilson_interval(correct, len(sample))
            lines.append(f"| {fault} | {condition} | {correct / len(sample):.1%} ({lo:.1%}–{hi:.1%}) | {silent / len(sample):.1%} |")
    lines.extend(["", "## Ablation results", "", "| Fault | Condition | Success rate |", "|---|---|---:|"])
    for fault in faults:
        for condition in conditions:
            if condition.startswith(("ablation", "without")):
                sample = group(fault, condition)
                if sample:
                    lines.append(f"| {fault} | {condition} | {sum(row['outcome'] == 'correct' for row in sample) / len(sample):.1%} |")
    lines.extend(["", "## Overhead", "", "| Condition | Mean extra calls | Mean virtual latency (s) |", "|---|---:|---:|"])
    for condition in conditions:
        sample = [row for row in rows if row["condition"] == condition]
        if sample:
            lines.append(f"| {condition} | {sum(r['extra_calls'] for r in sample) / len(sample):.2f} | {sum(r['virtual_latency_s'] for r in sample) / len(sample):.2f} |")
    lines.extend(["", "## What did not work", ""])
    for fault in faults:
        base, resilient = group(fault, "baseline"), group(fault, "resilient")
        if not base or not resilient:
            continue
        b = sum(r["outcome"] == "correct" for r in base) / len(base)
        r = sum(row["outcome"] == "correct" for row in resilient) / len(resilient)
        silent = sum(row["outcome"] == "wrong_silent" for row in resilient) / len(resilient)
        bhi = wilson_interval(round(b * len(base)), len(base))[1]
        rlo = wilson_interval(round(r * len(resilient)), len(resilient))[0]
        if silent > .05 or not (rlo > bhi):
            lines.append(f"- `{fault}`: resilient success {r:.1%}; silent failures {silent:.1%}. The measured improvement is not clearly separated from baseline or silent failures exceed 5%.")
    if not any(line.startswith("- `") for line in lines):
        lines.append("- No remaining issue met the report's configured thresholds in this sample.")
    lines.extend(["", "## Charts", "", "![Success curves](degradation_curves.png)", "", "![Outcome mix](outcomes_stacked.png)", "", "![Ablation heatmap](ablation_heatmap.png)", ""])

    # Success by rate, one small panel per fault.
    rates = sorted({row["rate"] for row in rows})
    fig, axes = plt.subplots(max(1, len(faults)), 1, figsize=(8, max(3, 2.6 * len(faults))), squeeze=False)
    for ax, fault in zip(axes[:, 0], faults):
        for condition in conditions:
            ys = []
            for current_rate in rates:
                sample = [row for row in rows if row["fault"] == fault and row["condition"] == condition and row["rate"] == current_rate]
                ys.append(sum(row["outcome"] == "correct" for row in sample) / len(sample) if sample else float("nan"))
            ax.plot(rates, ys, marker="o", label=condition)
        ax.set_title(fault)
        ax.set_ylim(-.05, 1.05)
        ax.set_ylabel("Success rate")
        ax.legend(fontsize="small")
    axes[-1, 0].set_xlabel("Fault rate")
    fig.tight_layout()
    fig.savefig(charts / "degradation_curves.png", dpi=140)
    plt.close(fig)

    selected = [row for row in rows if row["rate"] == rate and row["condition"] in ("baseline", "resilient")]
    counts = {condition: Counter(row["outcome"] for row in selected if row["condition"] == condition) for condition in ("baseline", "resilient")}
    outcomes = ["correct", "wrong_silent", "failed_loud", "budget_exceeded"]
    fig, ax = plt.subplots(figsize=(7, 4))
    bottoms = [0, 0]
    for outcome in outcomes:
        values = []
        for condition in ("baseline", "resilient"):
            total = sum(counts[condition].values())
            values.append(counts[condition][outcome] / total if total else 0)
        ax.bar(["baseline", "resilient"], values, bottom=bottoms, label=outcome)
        bottoms = [x + y for x, y in zip(bottoms, values)]
    ax.set_ylabel("Share of runs")
    ax.legend()
    fig.tight_layout()
    fig.savefig(charts / "outcomes_stacked.png", dpi=140)
    plt.close(fig)

    mitigation_names = [c for c in conditions if c.startswith(("ablation", "without"))]
    matrix = []
    for fault in faults:
        row_values = []
        for condition in mitigation_names:
            base, trial = group(fault, "baseline"), group(fault, condition)
            succ = lambda rs: sum(x["outcome"] == "correct" for x in rs) / len(rs) if rs else 0
            row_values.append(succ(trial) - succ(base))
        matrix.append(row_values)
    fig, ax = plt.subplots(figsize=(max(6, len(mitigation_names)), max(3, len(faults) * .55)))
    if mitigation_names:
        image = ax.imshow(matrix, cmap="RdYlGn", vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(len(mitigation_names)), mitigation_names, rotation=30, ha="right")
        ax.set_yticks(range(len(faults)), faults)
        fig.colorbar(image, ax=ax, label="Success-rate gain")
    else:
        ax.text(.5, .5, "No ablation conditions in this run", ha="center", va="center")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(charts / "ablation_heatmap.png", dpi=140)
    plt.close(fig)

    report = "\n".join(lines)
    Path(out_path).write_text(report, encoding="utf-8")
    return report
