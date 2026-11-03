"""Turn findings into a draft of trace-findings.md (lab step 1) with the deck's first fix beside each (s.9)."""
from .analyze import find_patterns, totals
from .spans import by_trace

FIRST_FIX = {
    "loop": "Add a stop condition and a step cap (Module 10 guard); say when to stop in the instructions",
    "retry storm": "Circuit breaker; short deterministic error text; prune failed attempts from context",
    "empty retrieval": "Strengthen the 'not found' rule; check whether the content exists at all",
    "bloated payload": "Extract only the fields the agent needs before it sees the tool output",
    "context growth": "Summarise older turns; keep a stable prompt prefix so it can be cached",
}


def question_of(spans):
    for s in spans:
        if s.kind == "agent" and "lab.user_question" in s.attrs:
            return s.attrs["lab.user_question"]
    return ""


def render(files):
    """files: {run name: [Span, ...]} -> markdown"""
    lines = ["# Trace findings (script draft, not your answer)", "",
             "| Run | Question | Model calls | Tool calls | Tokens in / out | Seconds |", "|---|---|---|---|---|---|"]
    found = []
    for name, spans in files.items():
        for trace in by_trace(spans).values():
            t = totals(trace)
            lines.append(f"| {name} | {question_of(trace)} | {t['llm_calls']} | {t['tool_calls']} "
                         f"| {t['tokens_in']} / {t['tokens_out']} | {t['ms'] / 1000:.1f} |")
            found += [(name, f) for f in find_patterns(trace)]
    lines += ["", "| Run | Pattern | Step to open in the viewer | Evidence | First fix |", "|---|---|---|---|---|"]
    for name, f in found:
        lines.append(f"| {name} | {f.pattern} | {f.step} | {f.evidence} | {FIRST_FIX[f.pattern]} |")
    lines += ["", "Not detected by this script: **wrong tool**. Read the tool calls against the question yourself.", ""]
    return "\n".join(lines)
