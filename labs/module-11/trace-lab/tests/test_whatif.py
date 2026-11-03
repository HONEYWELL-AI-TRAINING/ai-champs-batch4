import pytest

from tracelab.analyze import llm_calls
from tracelab.make_samples import RUNS, to_otlp
from tracelab.spans import load_otlp
from tracelab.whatif import trim


def spans_for(name):
    return load_otlp(to_otlp("f" * 32, RUNS[name]))


def test_trimming_lowers_every_later_call_by_the_same_amount():
    spans = spans_for("run-c-bloated")
    new, saved = trim(spans, "list_commits", 600)
    assert saved == 13400
    assert [c.tokens_in for c in llm_calls(new)] == [700, 1350, 1950]


def test_trim_does_not_change_the_original_spans():
    spans = spans_for("run-c-bloated")
    trim(spans, "list_commits", 600)
    assert [c.tokens_in for c in llm_calls(spans)] == [700, 14750, 15350]


def test_trimming_to_more_than_it_added_changes_nothing():
    new, saved = trim(spans_for("run-c-bloated"), "list_commits", 20_000)
    assert saved == 0 and [c.tokens_in for c in llm_calls(new)] == [700, 14750, 15350]


def test_unknown_tool_is_an_error_not_a_silent_zero():
    with pytest.raises(SystemExit):
        trim(spans_for("run-c-bloated"), "nope", 10)
