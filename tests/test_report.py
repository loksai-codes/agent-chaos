from agent_chaos.report import build_report


def test_report_includes_per_tool_outcomes_and_wrong_value_silence(tmp_path):
    rows = [
        {"task": "one", "fault": "wrong_value", "rate": .2, "condition": "baseline", "outcome": "wrong_silent", "tools_used": ["get_price"], "extra_calls": 0, "virtual_latency_s": 0},
        {"task": "two", "fault": "wrong_value", "rate": .2, "condition": "resilient", "outcome": "correct", "tools_used": ["get_price", "get_exchange_rate"], "extra_calls": 0, "virtual_latency_s": 0},
        {"task": "three", "fault": "wrong_value", "rate": .2, "condition": "resilient", "outcome": "failed_loud", "tools_used": ["get_price"], "extra_calls": 0, "virtual_latency_s": 0},
    ]
    report = build_report({"seed": 10, "rows": rows}, tmp_path / "report.md", tmp_path / "charts")

    assert "## Outcomes by tool" in report
    assert "| get_price | baseline | 0.0% (0/1) | 100.0% (1/1) | 0.0% (0/1) |" in report
    assert "## Wrong-value silent failures by tool (rate 0.2)" in report
    assert "| get_price | baseline | 100.0% (1/1) |" in report
