import json

import pytest

from tracelab.make_samples import RUNS, document
from tracelab.report import FIRST_FIX, render
from tracelab.sdk_to_otlp import convert
from tracelab.spans import load_otlp, load_sdk_jsonl


def test_report_lists_each_finding_with_its_fix_and_question():
    md = render({n: load_otlp(document(n)) for n in RUNS})
    for pattern, fix in FIRST_FIX.items():
        assert f"| {pattern} |" in md and fix in md
    assert "run-a-healthy | loop" not in md
    assert "wrong tool" in md.lower()
    assert "Draft release notes for v1.3." in md


def test_converted_sdk_trace_reads_back_the_same():
    lines = [json.dumps({"type": "span", "traceId": "t", "spanId": "2", "parentSpanId": "1", "name": "chat m",
                         "startTime": [100, 5], "endTime": [100, 9_000_005], "status": {"code": 2},
                         "attributes": {"gen_ai.operation.name": "chat", "gen_ai.usage.input_tokens": 7,
                                        "gen_ai.usage.output_tokens": 3, "gen_ai.response.finish_reasons": ["stop"]}}),
             json.dumps({"type": "span", "traceId": "t", "spanId": "9", "name": "session.timing.x",
                         "startTime": [100, 0], "endTime": [100, 0], "status": {"code": 0}, "attributes": {}})]
    direct = load_sdk_jsonl(lines)
    via_otlp = load_otlp(convert(lines))
    assert len(direct) == len(via_otlp) == 1
    assert (direct[0].tokens_in, direct[0].tokens_out, direct[0].error) == (via_otlp[0].tokens_in, via_otlp[0].tokens_out, via_otlp[0].error) == (7, 3, True)
    assert direct[0].ms == pytest.approx(9) and via_otlp[0].ms == pytest.approx(9, abs=0.01)
