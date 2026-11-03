import json

import pytest

from tracelab.make_samples import RUNS, document, to_otlp
from tracelab.spans import by_trace, load_otlp, load_sdk_jsonl

HASH = "911bf17675ea868ed7da531536bd0e072772dc2c1051cba430e29d30db2cd4cf"


def sdk_line(name, op, span_id, parent=None, status=0, **attrs):
    return json.dumps({"type": "span", "traceId": "t1", "spanId": span_id, "parentSpanId": parent, "name": name,
                       "startTime": [100, 0], "endTime": [100, 5_000_000], "status": {"code": status},
                       "attributes": {**({"gen_ai.operation.name": op} if op else {}), **attrs}})


def test_otlp_kinds_tokens_and_tool_names():
    spans = load_otlp(to_otlp("a" * 32, RUNS["run-a-healthy"]))
    assert [s.kind for s in spans] == ["agent", "llm", "tool", "llm", "tool", "llm"]
    llm = [s for s in spans if s.kind == "llm"]
    assert (llm[0].tokens_in, llm[0].tokens_out) == (800, 60)
    assert [s.tool for s in spans if s.kind == "tool"] == ["search_docs", "get_build_status"]


def test_otlp_error_status_is_read():
    spans = load_otlp(to_otlp("b" * 32, RUNS["run-d-retry-storm"]))
    assert sum(s.error for s in spans if s.kind == "tool") == 3
    assert not any(s.error for s in spans if s.kind == "llm")


def test_durations_are_milliseconds():
    spans = load_otlp(to_otlp("c" * 32, RUNS["run-a-healthy"]))
    assert [s.ms for s in spans if s.kind == "llm"] == pytest.approx([900, 1100, 1300], abs=0.01)


def test_sdk_file_drops_timing_noise_and_metrics():
    lines = [sdk_line("session.timing.x", None, "1"),
             json.dumps({"type": "metric", "name": "gen_ai.client.operation.duration"}),
             sdk_line("invoke_agent", "invoke_agent", "2"),
             sdk_line("chat m", "chat", "3", parent="2", **{"gen_ai.usage.input_tokens": 10, "gen_ai.usage.output_tokens": 5})]
    spans = load_sdk_jsonl(lines)
    assert [s.kind for s in spans] == ["agent", "llm"]
    assert spans[1].tokens_in == 10 and spans[1].ms == pytest.approx(5)


def test_hashed_tool_name_is_labelled_not_mistaken_for_a_name():
    spans = load_sdk_jsonl([sdk_line(f"execute_tool {HASH}", "execute_tool", "4", **{"gen_ai.tool.name": HASH})])
    assert spans[0].tool == "hashed-911bf176"


def test_sdk_error_status():
    spans = load_sdk_jsonl([sdk_line("execute_tool x", "execute_tool", "5", status=2, **{"gen_ai.tool.name": "x"})])
    assert spans[0].error


def test_by_trace_groups_and_orders():
    a = load_otlp(to_otlp("a" * 32, RUNS["run-a-healthy"]))
    e = load_otlp(to_otlp("e" * 32, RUNS["run-e-empty-retrieval"]))
    runs = by_trace(e + a)
    assert set(runs) == {"a" * 32, "e" * 32}
    assert all(r == sorted(r, key=lambda s: s.start_ms) for r in runs.values())


def test_shipped_trace_files_match_the_generator():
    # traces/*.json are what learners open. If you change make_samples.py, run it again.
    import os
    here = os.path.dirname(os.path.dirname(__file__))
    for name in RUNS:
        with open(os.path.join(here, "traces", f"{name}.json"), encoding="utf-8") as f:
            assert json.load(f) == document(name), f"{name}.json is stale: python -m tracelab.make_samples"
