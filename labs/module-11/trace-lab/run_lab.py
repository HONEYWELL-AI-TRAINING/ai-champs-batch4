"""Find the deck's failure patterns in trace files and write a DRAFT table (Lab 01, step 1).

  python run_lab.py                       # reads traces/*.json  ->  lab11/findings-draft.md
  python run_lab.py trace.jsonl           # your own agent's trace (Lab 03)

The draft is not your answer. Open each flagged step yourself and write lab11/trace-findings.md
in your own words (the deck's 'done when': each finding cites a step in a trace)."""
import glob
import os
import sys

from tracelab.report import render
from tracelab.spans import load_file

paths = sys.argv[1:] or sorted(glob.glob("traces/*.json"))
if not paths:
    sys.exit("no traces found: run  python -m tracelab.make_samples  first")
md = render({os.path.splitext(os.path.basename(p))[0]: load_file(p) for p in paths})
os.makedirs("lab11", exist_ok=True)
with open(os.path.join("lab11", "findings-draft.md"), "w", encoding="utf-8") as f:
    f.write(md)
print(md)
print("(written to lab11/findings-draft.md)")
