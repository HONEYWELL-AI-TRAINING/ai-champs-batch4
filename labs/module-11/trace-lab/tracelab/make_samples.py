"""Writes six INVENTED sample runs as OTLP/JSON into traces/. Not real data (deck s.5: 'illustrative shape').
Step tuples:  ("llm", ms, tokens_in, tokens_out)
              ("tool", name, ms, arguments, result, failed)
Run:  python -m tracelab.make_samples"""
import json
import os

SEARCH = lambda q, res, ms=140: ("tool", "search_docs", ms, json.dumps({"query": q}), res, False)
BUILD = lambda ms=80: ("tool", "get_build_status", ms, json.dumps({"build_id": "b-1234"}), '{"status": "failed"}', False)
HIT = '[{"source": "runbook-payments.md", "chunk_id": "s4"}]'

RUNS = {
    "run-a-healthy": [
        ("llm", 900, 800, 60), SEARCH("rollback window", HIT), ("llm", 1100, 1500, 90), BUILD(),
        ("llm", 1300, 1750, 120)],
    "run-b-loop": [
        ("llm", 900, 900, 40), BUILD(), ("llm", 700, 1200, 30), BUILD(), ("llm", 700, 1500, 30), BUILD(),
        ("llm", 700, 1800, 30), BUILD(), ("llm", 700, 2100, 30), BUILD(), ("llm", 700, 2400, 30)],
    "run-c-bloated": [
        ("llm", 800, 700, 50),
        ("tool", "list_commits", 900, json.dumps({"range": "v1.2..v1.3"}), "<14000 tokens of raw commits>", False),
        ("llm", 2600, 14750, 400), BUILD(60), ("llm", 2400, 15350, 300)],
    "run-d-retry-storm": [
        ("llm", 800, 800, 50),
        ("tool", "create_issue", 300, json.dumps({"label": "bug!"}), '{"error": "422 invalid label"}', True),
        ("llm", 600, 900, 40),
        ("tool", "create_issue", 300, json.dumps({"label": "bug "}), '{"error": "422 invalid label"}', True),
        ("llm", 600, 1000, 40),
        ("tool", "create_issue", 300, json.dumps({"label": "Bug"}), '{"error": "422 invalid label"}', True),
        ("llm", 900, 1100, 90)],
    "run-e-empty-retrieval": [
        ("llm", 900, 800, 60), SEARCH("refund approval limit", "[]", 90), ("llm", 1000, 1000, 120)],
    "run-f-wrong-tool": [   # asks about a policy, calls the build tool: no number shows it
        ("llm", 900, 800, 60),
        ("tool", "get_build_status", 80, json.dumps({"build_id": "b-0000"}), '{"error": "no build b-0000"}', True),
        ("llm", 1000, 950, 110)],
}

# What the user asked in each run. A trace shows what the agent DID; you need the question to judge
# whether it did the right thing (the wrong-tool run is only visible against its question).
QUESTIONS = {
    "run-a-healthy": "What is our payments rollback window, and did build b-1234 pass?",
    "run-b-loop": "Why did build b-1234 fail?",
    "run-c-bloated": "Draft release notes for v1.3.",
    "run-d-retry-storm": "Open a bug issue for the failing checkout test.",
    "run-e-empty-retrieval": "What is the refund approval limit?",
    "run-f-wrong-tool": "How long do we keep payment logs?",
}


def _attr(k, v):
    key = "intValue" if isinstance(v, int) and not isinstance(v, bool) else "stringValue"
    return {"key": k, "value": {key: str(v) if key == "intValue" else v}}


def to_otlp(trace_id, steps, t0_ms=1_800_000_000_000, question=None):
    spans, t, n = [], t0_ms, 0

    def add(name, start, dur, attrs, parent, error=False):
        nonlocal n
        n += 1
        spans.append({"traceId": trace_id, "spanId": f"{n:016x}", "parentSpanId": parent, "name": name,
                      "startTimeUnixNano": str(start * 1_000_000), "endTimeUnixNano": str((start + dur) * 1_000_000),
                      "attributes": [_attr(k, v) for k, v in attrs.items()],
                      "status": {"code": 2 if error else 1}})
        return spans[-1]

    root_attrs = {"gen_ai.operation.name": "invoke_agent"}
    if question:
        root_attrs["lab.user_question"] = question
    root = add("invoke_agent", t, 0, root_attrs, "")
    for st in steps:
        if st[0] == "llm":
            _, ms, tin, tout = st
            add("chat sample-model", t, ms, {"gen_ai.operation.name": "chat", "gen_ai.request.model": "sample-model",
                                              "gen_ai.usage.input_tokens": tin, "gen_ai.usage.output_tokens": tout},
                root["spanId"])
        else:
            _, name, ms, args, res, failed = st
            add(f"execute_tool {name}", t, ms, {"gen_ai.operation.name": "execute_tool", "gen_ai.tool.name": name,
                                                "gen_ai.tool.call.arguments": args, "gen_ai.tool.call.result": res},
                root["spanId"], failed)
        t += ms + 5
    root["endTimeUnixNano"] = str(t * 1_000_000)
    return {"resourceSpans": [{"scopeSpans": [{"spans": spans}]}]}


def document(name):
    """The OTLP/JSON document for one sample run (stable trace ids: run order)."""
    i = list(RUNS).index(name) + 1
    return to_otlp(f"{i:032x}", RUNS[name], question=QUESTIONS[name])


def main(out="traces"):
    os.makedirs(out, exist_ok=True)
    for name in RUNS:
        with open(os.path.join(out, f"{name}.json"), "w", encoding="utf-8") as f:
            json.dump(document(name), f, indent=1)
            f.write("\n")


if __name__ == "__main__":
    main()
