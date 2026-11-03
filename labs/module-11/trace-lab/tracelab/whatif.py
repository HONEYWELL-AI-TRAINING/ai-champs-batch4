"""What if a tool's output were trimmed before the model saw it? (Lab 01, step 4)

    python -m tracelab.whatif traces/run-c-bloated.json --tool list_commits --to 600

Method (same assumption as analyze.added_tokens): every model call resends the whole history, so tokens
a tool result adds to the context are paid again on every later call. Trimming that result to N tokens
lowers the input of every model call after it by (added - N). Output tokens are assumed unchanged.
It is an estimate. Re-run the real agent with the fix to confirm."""
import argparse
from dataclasses import replace

from .analyze import added_tokens, llm_calls
from .spans import by_trace, load_file


def trim(spans, tool, to_tokens):
    """Return (new spans, tokens removed from the context). Only the first matching tool step is trimmed."""
    spans = [replace(s) for s in spans]
    rows = added_tokens(spans)
    for i, (_, added, producer) in enumerate(rows):
        if producer is not None and producer.tool == tool:
            saved = max(0, added - to_tokens)
            calls = llm_calls(spans)
            for c in calls[i:]:
                c.tokens_in -= saved
            return spans, saved
    raise SystemExit(f"no step of tool '{tool}' feeds a model call in this trace")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--tool", required=True)
    ap.add_argument("--to", type=int, required=True, help="tokens the trimmed result will still add")
    a = ap.parse_args()
    for spans in by_trace(load_file(a.file)).values():
        new, saved = trim(spans, a.tool, a.to)
        before, after = llm_calls(spans), llm_calls(new)
        print(f"{a.tool} result trimmed by {saved} tokens (it will still add {a.to})\n")
        print("| Model call | Input before | Input after |\n|---|---|---|")
        for n, (b, c) in enumerate(zip(before, after), 1):
            print(f"| {n} | {b.tokens_in} | {c.tokens_in} |")
        tb, ta = sum(c.tokens_in for c in before), sum(c.tokens_in for c in after)
        out = sum(c.tokens_out for c in before)
        print(f"\nInput tokens per run: {tb} -> {ta} ({(ta - tb) / tb:+.0%}).  Output tokens per run: {out} (unchanged).")


if __name__ == "__main__":
    main()
