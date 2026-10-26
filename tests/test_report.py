from agent_chaos.report import build_report


def test_report_includes_per_tool_outcomes_and_wrong_value_silence(tmp_path):
    rows = [
        {"task": "one", "fault": "wrong_value", "rate": .2, "condition": "baseline", "outcome": "wrong_silent", "tools_used": ["get_price"], "extra_calls": 0, "virtual_latency_s": 0},
        {"task": "two", "fault": "wrong_value", "rate": .2, "condition": "resilient", "outcome": "correct", "tools_used": ["get_price", "get_exchange_rate"], "extra_calls": 0, "virtual_latency_s": 0},
        {"task": "three", "fault": "wrong_value", "rate": .2, "condition": "resilient", "outcome": "failed_loud", "tools_used": ["get_price"], "extra_calls": 0, "virtual_latency_s": 0},
        {"task": "four", "fault": "wrong_value", "rate": 0.0, "condition": "baseline", "outcome": "correct", "tools_used": ["get_price"], "extra_calls": 0, "retry_extra_calls": 0, "redundancy_extra_calls": 0, "virtual_latency_s": 0},
    ]
    report = build_report({"seed": 10, "rows": rows}, tmp_path / "report.md", tmp_path / "charts")

    assert "## Outcomes by tool" in report
    assert "| get_price | baseline | 50.0% (1/2) | 50.0% (1/2) | 0.0% (0/2) |" in report
    assert "## Wrong-value silent failures by tool (rate 0.2)" in report
    assert "| get_price | baseline | 100.0% (1/1) |" in report
    assert "Ablations not run in this experiment" in report
    assert "Fault rates: 0, 0.2." in report
    assert "| wrong_value | 0 | baseline |" in report
    assert "| Fault | Rate | Condition | Retry extra calls | Redundancy extra calls |" in report
    for chart_name in ("degradation_curves.png", "outcomes_stacked.png", "ablation_heatmap.png"):
        assert (tmp_path / "charts" / chart_name).is_file()
        assert (tmp_path / "charts" / chart_name).stat().st_size > 0
        assert f"](charts/{chart_name})" in report
