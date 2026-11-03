"""Quality and control signals (deck s.8) from reviewer decisions.

    python -m tracelab.decisions data/reviewer-decisions.csv

CSV columns: run, decision (accepted | edited | rejected), review_min, edit_min, later_defect (0/1), run_failed (0/1).
  accepted = kept as-is   edited = kept after light edits   rejected = thrown away"""
import csv
import sys


def signals(rows):
    n = len(rows)
    kept = [r for r in rows if r["decision"] in ("accepted", "edited")]
    edited = [r for r in rows if r["decision"] == "edited"]
    rejected = [r for r in rows if r["decision"] == "rejected"]
    f = lambda k, rs: sum(float(r[k]) for r in rs)
    return {
        "runs": n,
        "kept": len(kept),
        "acceptance_rate": len(kept) / n,
        "override_rate": (len(edited) + len(rejected)) / n,
        "failure_rate": f("run_failed", rows) / n,
        "review_min_per_run": f("review_min", rows) / n,
        "edit_min_per_accepted": f("edit_min", kept) / len(kept) if kept else 0.0,
        "later_defects_per_accepted": f("later_defect", kept) / len(kept) if kept else 0.0,
    }


def load(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main(path):
    s = signals(load(path))
    print(f"runs                         {s['runs']}")
    print(f"kept (accepted or edited)    {s['kept']}")
    print(f"acceptance rate              {s['acceptance_rate']:.0%}   (kept / runs)")
    print(f"override + edit rate         {s['override_rate']:.0%}   ((edited + rejected) / runs)")
    print(f"failure rate                 {s['failure_rate']:.0%}   (runs that errored or looped)")
    print(f"review minutes per run       {s['review_min_per_run']:.2f}")
    print(f"edit minutes per kept output {s['edit_min_per_accepted']:.2f}")
    print(f"later defects per kept       {s['later_defects_per_accepted']:.2f}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
