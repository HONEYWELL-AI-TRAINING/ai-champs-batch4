"""Cost per accepted output, before and after (Lab 01, step 5).

  python roi_calc.py                      # reads lab11/roi-inputs.json, else templates/roi-inputs.json
  python roi_calc.py path/to/inputs.json

Input file: {"before": {...all Scenario fields...}, "after": {...only the fields the fix changes...}}
You may give "acceptance_rate" (0-1) instead of "accepted"; accepted is then runs x acceptance_rate, rounded.
Keys starting with "_" are your notes and are ignored."""
import json
import os
import sys
from dataclasses import fields

from tracelab.roi import Scenario, sweep


def scenario(d):
    d = {k: v for k, v in d.items() if not k.startswith("_")}
    if "acceptance_rate" in d:
        d["accepted"] = round(d["runs"] * d.pop("acceptance_rate"))
    missing = [f.name for f in fields(Scenario) if f.name not in d]
    if missing:
        sys.exit(f"missing inputs: {', '.join(missing)}")
    return Scenario(**d)


def load(path):
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    before = {k: v for k, v in doc["before"].items() if not k.startswith("_")}
    after = {**before, **{k: v for k, v in doc.get("after", {}).items() if not k.startswith("_")}}
    if "accepted" in doc.get("after", {}):
        after.pop("acceptance_rate", None)
    if "acceptance_rate" in doc.get("after", {}):
        after.pop("accepted", None)
    return scenario(before), scenario(after)


def row(label, s):
    be = s.breakeven_acceptance
    be = "never" if be is None else f"{be:.0%}"
    cpa = "n/a" if s.cost_per_accepted is None else f"{s.cost_per_accepted:.2f}"
    return (f"| {label} | {s.runs} | {s.accepted} | {s.acceptance_rate:.0%} | {s.token_cost_per_run:.3f} "
            f"| {s.total_cost:.2f} | {cpa} | {s.net:.2f} | {be} |")


def main(path):
    before, after = load(path)
    print(f"inputs: {path}\n")
    print("| | Runs | Accepted | Acceptance | Token cost per run | Total cost | Cost per accepted | Net vs manual | Break-even acceptance |")
    print("|---|---|---|---|---|---|---|---|---|")
    print(row("Before", before))
    print(row("After", after))
    print("\nIf review takes longer or shorter than assumed (cost per accepted output, after the fix):")
    for minutes, cost in sweep(after, "review_min_per_run", [1, 3, 6, 10]):
        print(f"  review {minutes:>2} min/run -> {cost:.2f}")
    print("\nIf more or fewer outputs were accepted (same runs, same cost per run):")
    for frac in (0.5, 0.75, 0.9):
        n = round(after.runs * frac)
        print(f"  accepted {n:>3} of {after.runs} ({frac:.0%}) -> {sweep(after, 'accepted', [n])[0][1]:.2f}")


if __name__ == "__main__":
    default = os.path.join("lab11", "roi-inputs.json")
    if not os.path.exists(default):
        default = os.path.join("templates", "roi-inputs.json")
    main(sys.argv[1] if len(sys.argv) > 1 else default)
