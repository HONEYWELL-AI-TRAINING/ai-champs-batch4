import pytest

from tracelab import analyze
from tracelab.analyze import added_tokens, find_patterns, totals
from tracelab.make_samples import RUNS, to_otlp
from tracelab.spans import load_otlp


def spans_for(name):
    return load_otlp(to_otlp("f" * 32, RUNS[name]))


@pytest.mark.parametrize("run,expected", [
    ("run-a-healthy", []),
    ("run-b-loop", ["loop", "context growth"]),
    ("run-c-bloated", ["bloated payload"]),
    ("run-d-retry-storm", ["retry storm"]),
    ("run-e-empty-retrieval", ["empty retrieval"]),
])
def test_each_sample_shows_exactly_its_patterns(run, expected):
    assert [f.pattern for f in find_patterns(spans_for(run))] == expected


def test_wrong_tool_is_not_detected_by_numbers():
    # Documents the limit: a human has to read this one. If you teach the script to catch it, change this test.
    assert find_patterns(spans_for("run-f-wrong-tool")) == []


def test_bloat_points_at_the_tool_that_caused_it():
    f = find_patterns(spans_for("run-c-bloated"))[0]
    assert f.step == "tool list_commits" and "14000" in f.evidence


def test_added_tokens_attributes_the_jump_to_the_step_between_calls():
    rows = added_tokens(spans_for("run-c-bloated"))
    assert [a for _, a, _ in rows] == [700, 14000, 200]
    assert rows[1][2].tool == "list_commits"


def test_loop_threshold_is_a_boundary():
    spans = spans_for("run-b-loop")
    tools = [s for s in spans if s.kind == "tool"]
    assert len(tools) == analyze.LOOP_MIN + 1
    kept = [s for s in spans if s.kind != "tool" or s in tools[: analyze.LOOP_MIN - 1]]
    assert "loop" not in [f.pattern for f in find_patterns(kept)]


def test_loop_needs_identical_arguments_when_they_are_captured():
    spans = spans_for("run-b-loop")
    for i, s in enumerate(t for t in spans if t.kind == "tool"):
        s.attrs["gen_ai.tool.call.arguments"] = f'{{"n": {i}}}'
    assert "loop" not in [f.pattern for f in find_patterns(spans)]


def test_small_runs_are_not_called_bloated():
    spans = spans_for("run-c-bloated")
    for s in spans:
        if s.kind == "llm":
            s.tokens_in //= 100
    assert "bloated payload" not in [f.pattern for f in find_patterns(spans)]


def test_a_short_run_with_a_huge_payload_is_still_bloated():
    spans = spans_for("run-e-empty-retrieval")          # two model calls, one tool call
    calls = [s for s in spans if s.kind == "llm"]
    calls[1].tokens_in = calls[0].tokens_in + calls[0].tokens_out + 5000   # the tool dumped 5,000 tokens
    assert [f.pattern for f in find_patterns(spans)] == ["empty retrieval", "bloated payload"]


def test_one_model_call_has_nothing_to_compare_and_does_not_crash():
    spans = spans_for("run-a-healthy")
    one = [s for s in spans if s.kind != "llm"] + [s for s in spans if s.kind == "llm"][:1]
    assert find_patterns(one) == []


def test_totals():
    t = totals(spans_for("run-a-healthy"))
    assert (t["llm_calls"], t["tool_calls"], t["tokens_in"], t["tokens_out"]) == (3, 2, 4050, 270)
