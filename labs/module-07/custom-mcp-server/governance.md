# Governance record — Build Insights MCP server

One page. A reviewer who cannot answer all seven questions from this page
should reject the server. Review this file in the same pull request as any new
tool.

| Question | Answer |
|----------|--------|
| **Owner** | Platform Engineering — `<team-alias>` (named human: `<name>`). Fixes and reviews tool changes. |
| **Purpose** | Let an agent answer "why did build X fail?" from CI data and runbooks. **Out of scope:** triggering/cancelling builds, reading source code, posting issues or comments, anything outside the CI domain. |
| **Tools** | `get_build_status(build_id)` — read. `list_recent_builds(status, limit)` — read. `get_test_failures(build_id)` — read, capped at 10 failures × 300 chars. `draft_followup_issue(build_id, title, summary)` — **write**: saves `drafts/<build_id>.md` locally, posts nothing. Resources: `docs://index`, `docs://runbooks/{name}` (read). Prompt: `explain_build_failure`. |
| **Data** | CI build metadata and test failure text (internal, not customer data) and the markdown files in `docs/`. The lab version uses mock data in `data.py`; a real version reaches the CI API only through `data.py`. No secrets, no PII, no production databases. |
| **Auth** | Lab: none needed (local stdio process, no network access). Real CI API: a **read-only, scoped token** supplied through a `${input:...}` variable or secret store — never in `mcp.json`, code, or logs. HTTP transport: bind to `127.0.0.1` only; anything shared needs OAuth/token auth in front of it before it leaves a developer machine. |
| **Approval** | Read tools: approve per session. `draft_followup_issue`: **approve every call, never auto-approve** (it is the only write; it is marked `readOnlyHint: false`). A human reviews the draft file before anything is filed. |
| **Off switch** | Developer: stop/remove `build-insights` from `.vscode/mcp.json` (or MCP: List Servers → Stop). Team: delete the file from the repo and the server entry from the allow-list. Org: MCP policy in Copilot settings. Data cleanup: `rm -r drafts/`. |

## Controls mapped to the threats

| Risk | Control in this server |
|------|------------------------|
| Prompt injection via tool results | Test failure text is returned as data, truncated to 300 chars; tool descriptions and server `instructions` say it is untrusted; the only write tool needs per-call approval; `b-1003` seeds an injection string to prove it. |
| Over-broad tools | Four narrow tools; no `run_query` / `run_command`; enable only what the task needs in the tools picker. |
| Untrusted server | Source is in this repo, reviewed by PR; the command in `mcp.json` is `uv run … python server.py`. |
| Leaked credentials | No credentials in the lab version; real ones via input variables. Audit log never records argument bodies beyond ids and titles. |
| No audit trail | Every tool call logs `AUDIT tool=… build_id=…` to stderr (visible via *Show Output*). Named owner above. |
| Path traversal / bad input | `build_id` must match `^b-\d{4}$`; runbook names must match `[a-z0-9-]{1,40}`; limits bounded with `ge`/`le`. |
| Context flooding | Output capped (`MAX_FAILURES`, `MAX_MESSAGE_CHARS`, `limit ≤ 20`). |

## Review log

| Date | Reviewer | Change | Decision |
|------|----------|--------|----------|
| | | Initial server | |
