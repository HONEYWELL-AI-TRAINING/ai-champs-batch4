"""Load agent traces into one small shape. Reads OTLP/JSON (what trace viewers take) and the
JSON-lines file the Copilot runtime writes with telemetry={"exporter_type": "file", ...}."""
import json
import re
from dataclasses import dataclass, field

ERROR = 2  # OpenTelemetry status code for "error"


@dataclass
class Span:
    trace_id: str
    id: str
    parent: str | None
    name: str
    kind: str                 # agent | llm | tool | other
    start_ms: float
    end_ms: float
    tokens_in: int = 0
    tokens_out: int = 0
    error: bool = False
    tool: str | None = None
    attrs: dict = field(default_factory=dict)

    @property
    def ms(self):
        return self.end_ms - self.start_ms


KINDS = {"invoke_agent": "agent", "chat": "llm", "text_completion": "llm",
         "execute_tool": "tool", "retrieval": "tool"}


def _span(trace_id, sid, parent, name, start_ms, end_ms, attrs, status):
    op = attrs.get("gen_ai.operation.name")
    tool = attrs.get("gen_ai.tool.name")
    if tool and re.fullmatch(r"[0-9a-f]{64}", tool):   # runtime hides names unless capture_content=True
        tool = "hashed-" + tool[:8]
    return Span(trace_id, sid, parent or None, name, KINDS.get(op, "other"), start_ms, end_ms,
                int(attrs.get("gen_ai.usage.input_tokens", 0) or 0),
                int(attrs.get("gen_ai.usage.output_tokens", 0) or 0),
                status == ERROR or status == "STATUS_CODE_ERROR", tool, attrs)


def _otlp_value(v):
    for key in ("stringValue", "intValue", "doubleValue", "boolValue"):
        if key in v:
            return int(v[key]) if key == "intValue" else v[key]
    return None


def load_otlp(doc):
    """OTLP/JSON: {"resourceSpans": [{"scopeSpans": [{"spans": [...]}]}]}"""
    out = []
    for rs in doc.get("resourceSpans", []):
        for ss in rs.get("scopeSpans", []):
            for s in ss.get("spans", []):
                attrs = {a["key"]: _otlp_value(a["value"]) for a in s.get("attributes", [])}
                out.append(_span(s["traceId"], s["spanId"], s.get("parentSpanId"), s["name"],
                                 int(s["startTimeUnixNano"]) / 1e6, int(s["endTimeUnixNano"]) / 1e6,
                                 attrs, s.get("status", {}).get("code")))
    return out


def load_sdk_jsonl(lines):
    """One JSON object per line; keep spans, drop metrics and the runtime's session.timing.* noise."""
    out = []
    for line in lines:
        r = json.loads(line)
        if r.get("type") != "span" or "gen_ai.operation.name" not in r["attributes"]:
            continue
        to_ms = lambda t: t[0] * 1e3 + t[1] / 1e6
        out.append(_span(r["traceId"], r["spanId"], r.get("parentSpanId"), r["name"],
                         to_ms(r["startTime"]), to_ms(r["endTime"]), r["attributes"],
                         r["status"]["code"]))
    return out


def load_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if text.lstrip().startswith('{"type"'):
        return load_sdk_jsonl(text.splitlines())
    return load_otlp(json.loads(text))


def by_trace(spans):
    runs = {}
    for s in spans:
        runs.setdefault(s.trace_id, []).append(s)
    return {k: sorted(v, key=lambda s: s.start_ms) for k, v in runs.items()}
