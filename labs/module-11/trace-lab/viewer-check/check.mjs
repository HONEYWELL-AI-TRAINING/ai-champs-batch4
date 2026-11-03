// node check.mjs ../traces/run-c-bloated.json [more files...]
// Prints what Agent Prism's own OTLP adapter makes of a trace: title, category, tokens, status per span.
import fs from "node:fs";
import { openTelemetrySpanAdapter, getTotalTokens } from "@evilmartians/agent-prism-data";

for (const file of process.argv.slice(2)) {
  const spans = openTelemetrySpanAdapter.convertRawDocumentsToSpans(JSON.parse(fs.readFileSync(file, "utf8")));
  const show = (s, depth = 0) => {
    const tokens = s.tokenUsage ? getTotalTokens(s.tokenUsage) : "-";
    console.log(`${"  ".repeat(depth)}${s.title} | ${s.type} | tokens ${tokens} | ${s.status}`);
    (s.children ?? []).forEach((c) => show(c, depth + 1));
  };
  console.log(file);
  spans.forEach((s) => show(s));
}
