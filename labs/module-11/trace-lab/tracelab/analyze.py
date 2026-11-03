"""Spot the deck's failure patterns (s.7) and token leaks (s.9) in a trace.
Thresholds are starting points. Set yours from your own baseline (s.8)."""
from dataclasses import dataclass

LOOP_MIN = 4        # same tool (same arguments, when captured) this many times in one run
RETRY_MIN = 3       # this many failed tool calls in one run
BLOAT_SHARE = 0.6   # one step adds this share of all the tokens added during the run ...
BLOAT_MIN_TOKENS = 2000  # ... and added at least this many tokens
GROWTH_RATIO = 2.5  # last call's input vs first call's input


@dataclass
class Finding:
    pattern: str
    step: str       # which span to open in the viewer
    evidence: str


def llm_calls(spans):
    return [s for s in spans if s.kind == "llm"]


def added_tokens(spans):
    """Approximation: input tokens a call added beyond the previous call's input + output.
    Assumes the full history is resent each call. The surplus is whatever the step between them
    put into context, which is usually a tool result. Returns [(call, added, producing tool span)]."""
    calls, rows, prev = llm_calls(spans), [], None
    for c in calls:
        added = c.tokens_in if prev is None else max(0, c.tokens_in - prev.tokens_in - prev.tokens_out)
        producer = None
        if prev is not None:
            between = [s for s in spans if s.kind == "tool" and prev.end_ms <= s.start_ms < c.start_ms]
            producer = between[-1] if between else None
        rows.append((c, added, producer))
        prev = c
    return rows


def totals(spans):
    calls = llm_calls(spans)
    return {"llm_calls": len(calls), "tool_calls": sum(s.kind == "tool" for s in spans),
            "tokens_in": sum(c.tokens_in for c in calls), "tokens_out": sum(c.tokens_out for c in calls),
            "ms": max((s.end_ms for s in spans), default=0) - min((s.start_ms for s in spans), default=0)}


def find_patterns(spans):
    out, tools = [], [s for s in spans if s.kind == "tool"]

    groups = {}
    for t in tools:
        groups.setdefault((t.tool, t.attrs.get("gen_ai.tool.call.arguments")), []).append(t)
    for (name, args), g in groups.items():
        if len(g) >= LOOP_MIN:
            out.append(Finding("loop", f"tool {name}", f"called {len(g)}x" + (" with identical arguments" if args else "")))

    failed = [t for t in tools if t.error]
    if len(failed) >= RETRY_MIN:
        out.append(Finding("retry storm", f"tool {failed[0].tool}", f"{len(failed)} failed tool calls in one run"))

    for t in tools:
        res = t.attrs.get("gen_ai.tool.call.result")
        if res is not None and str(res).strip() in ("", "[]", "{}", "null"):
            out.append(Finding("empty retrieval", f"tool {t.tool}", "tool returned nothing; check the answer says so"))

    calls = llm_calls(spans)
    rows = added_tokens(spans)
    total_added = sum(a for _, a, _ in rows)
    bloated = False
    if len(calls) >= 2 and total_added:
        call, added, src = max(rows[1:], key=lambda r: r[1])   # row 0 is the prompt itself
        if added >= BLOAT_MIN_TOKENS and added / total_added >= BLOAT_SHARE:
            bloated = True
            out.append(Finding("bloated payload", f"tool {src.tool}" if src else "a step before a model call",
                               f"one step added {added} tokens, {added / total_added:.0%} of everything added in the run"))
    if not bloated and len(calls) >= 4 and calls[0].tokens_in and calls[-1].tokens_in / calls[0].tokens_in >= GROWTH_RATIO:
        out.append(Finding("context growth", "every model call after the first",
                           f"input grew {calls[0].tokens_in} to {calls[-1].tokens_in} tokens across {len(calls)} calls"))
    return out   # 'wrong tool' needs a human: nothing in the numbers says a tool could not answer
