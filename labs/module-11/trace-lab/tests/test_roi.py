import json
import os

import pytest

from roi_calc import load
from tracelab.decisions import load as load_rows, signals
from tracelab.roi import Scenario, sweep

HERE = os.path.dirname(os.path.dirname(__file__))
S = Scenario(runs=10, accepted=5, tokens_in_per_run=1_000_000, tokens_out_per_run=0, price_in_per_m=1.0,
             price_out_per_m=0.0, tooling_per_run=0.5, review_min_per_run=30, edit_min_per_accepted=60,
             rework_per_accepted=2.0, hourly_rate=10, manual_min_per_task=180)


def test_hand_checked_numbers():
    assert S.token_cost_per_run == 1.0
    assert S.fixed_per_run == 1.0 + 0.5 + 5.0          # tokens + tooling + 30 min of review at 10/h
    assert S.per_accepted == 10.0 + 2.0                # 60 min of editing + rework
    assert S.total_cost == 10 * 6.5 + 5 * 12.0         # 125
    assert S.cost_per_accepted == 25.0
    assert S.value_per_accepted == 30.0
    assert S.net == 5 * 30.0 - 125.0


def test_nothing_accepted_has_no_cost_per_accepted_not_zero():
    assert Scenario(**{**S.__dict__, "accepted": 0}).cost_per_accepted is None


def test_counting_generated_as_accepted_flatters_the_number():
    flattered = Scenario(**{**S.__dict__, "accepted": S.runs})
    assert flattered.cost_per_accepted < S.cost_per_accepted


def test_review_time_is_not_free():
    free = Scenario(**{**S.__dict__, "review_min_per_run": 0})
    assert free.cost_per_accepted < S.cost_per_accepted


def test_failed_runs_cost_money_even_when_nothing_more_is_accepted():
    more_failures = Scenario(**{**S.__dict__, "runs": 20})
    assert more_failures.total_cost > S.total_cost and more_failures.accepted == S.accepted


def test_breakeven_acceptance_gives_zero_net():
    rate = S.breakeven_acceptance
    at = Scenario(**{**S.__dict__, "accepted": S.runs * rate})
    assert at.net == pytest.approx(0)
    assert rate == pytest.approx(6.5 / (30.0 - 12.0))


def test_no_breakeven_when_each_accepted_output_costs_more_than_it_saves():
    assert Scenario(**{**S.__dict__, "manual_min_per_task": 60}).breakeven_acceptance is None


def test_sweep_changes_one_assumption_only():
    out = dict(sweep(S, "review_min_per_run", [0, 30, 60]))
    assert out[30] == S.cost_per_accepted and out[0] < out[30] < out[60]


def test_template_fix_only_touches_tokens():
    before, after = load(os.path.join(HERE, "templates", "roi-inputs.json"))
    assert (after.runs, after.accepted) == (before.runs, before.accepted) == (200, 150)
    assert after.tokens_in_per_run < before.tokens_in_per_run
    assert after.cost_per_accepted < before.cost_per_accepted


def test_template_lesson_tokens_fall_a_lot_cost_per_accepted_barely_moves():
    before, after = load(os.path.join(HERE, "templates", "roi-inputs.json"))
    assert 1 - after.token_cost_per_run / before.token_cost_per_run > 0.7
    assert 1 - after.cost_per_accepted / before.cost_per_accepted < 0.02


def test_acceptance_rate_input_becomes_a_count(tmp_path):
    doc = json.load(open(os.path.join(HERE, "templates", "roi-inputs.json"), encoding="utf-8"))
    doc["after"]["acceptance_rate"] = 0.9
    p = tmp_path / "in.json"
    p.write_text(json.dumps(doc))
    before, after = load(str(p))
    assert (before.accepted, after.accepted) == (150, 180)


def test_missing_input_is_named(tmp_path):
    doc = json.load(open(os.path.join(HERE, "templates", "roi-inputs.json"), encoding="utf-8"))
    del doc["before"]["hourly_rate"]
    p = tmp_path / "in.json"
    p.write_text(json.dumps(doc))
    with pytest.raises(SystemExit) as e:
        load(str(p))
    assert "hourly_rate" in str(e.value)


def test_signals_from_the_shipped_reviewer_decisions():
    s = signals(load_rows(os.path.join(HERE, "data", "reviewer-decisions.csv")))
    assert (s["runs"], s["kept"]) == (24, 18)
    assert s["acceptance_rate"] == 0.75 and s["override_rate"] == 0.5 and s["failure_rate"] == 0.125
    assert round(s["review_min_per_run"], 2) == 3.29 and round(s["edit_min_per_accepted"], 2) == 2.78
    assert round(s["later_defects_per_accepted"], 2) == 0.11
