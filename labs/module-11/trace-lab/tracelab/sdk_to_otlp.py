"""Convert the Copilot runtime's JSON-lines trace file to OTLP/JSON so a viewer can open it.
python -m tracelab.sdk_to_otlp trace.jsonl out.json"""
import json
import sys


def convert(lines):
    spans = []
    for line in lines:
        r = json.loads(line)
        if r.get("type") != "span" or "gen_ai.operation.name" not in r["attributes"]:
            continue
        nanos = lambda t: str(t[0] * 10**9 + t[1])
        attrs = []
        for k, v in r["attributes"].items():
            if isinstance(v, bool):
                attrs.append({"key": k, "value": {"boolValue": v}})
            elif isinstance(v, int):
                attrs.append({"key": k, "value": {"intValue": str(v)}})
            elif isinstance(v, float):
                attrs.append({"key": k, "value": {"doubleValue": v}})
            else:
                attrs.append({"key": k, "value": {"stringValue": v if isinstance(v, str) else json.dumps(v)}})
        spans.append({"traceId": r["traceId"], "spanId": r["spanId"], "parentSpanId": r.get("parentSpanId", ""),
                      "name": r["name"], "startTimeUnixNano": nanos(r["startTime"]),
                      "endTimeUnixNano": nanos(r["endTime"]), "attributes": attrs, "status": r["status"]})
    return {"resourceSpans": [{"scopeSpans": [{"spans": spans}]}]}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as src, open(sys.argv[2], "w", encoding="utf-8") as dst:
        json.dump(convert(src), dst, indent=1)
