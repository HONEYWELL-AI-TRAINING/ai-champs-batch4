# Build Insights — custom MCP server (Module 07, Labs 04–06)

A small, governed [FastMCP](https://gofastmcp.com) server that answers *"why did
build X fail?"* from (mock) CI data and runbooks. It exists to teach the shape
of a custom MCP server: narrow typed tools, a resource, a prompt, one guarded
write, and a governance page.

| Path | What |
|------|------|
| `server_minimal.py` | Lab 04 — the 20-line starter |
| `server.py` | Labs 05–06 — full server (4 tools, 2 resources, 1 prompt) |
| `data.py` | Mock CI data + the only "system of record" access point |
| `docs/` | Runbooks served as resources |
| `tests/test_server.py` | 14 automated checks (in-memory FastMCP client) |
| `vscode-mcp.json.example` | Copilot config (stdio) → copy to `.vscode/mcp.json` |
| `vscode-mcp-http.json.example` | Copilot config (Streamable HTTP) |
| `TESTING.md` | **Step-by-step: test with pytest, MCP Inspector and GitHub Copilot** |
| `governance.md` | One-page governance record |
| `test-notes.md` | Fill-in sheet for your test results |

## Quick start

```bash
uv sync
uv run pytest -q                           # 14 passed
uv run fastmcp dev inspector server.py     # Inspector UI (stdio)
uv run fastmcp run server.py -t http       # Streamable HTTP on 127.0.0.1:8000/mcp
```

Then follow [TESTING.md](TESTING.md). Requires Python ≥ 3.10, `uv`, Node.js
(for the Inspector), and FastMCP 4.x (pinned in `pyproject.toml` / `uv.lock`;
CLI flags differ in 2.x).

## Design rules this server demonstrates

One tool, one job · description written for the model · typed, bounded inputs ·
small structured output · read-only by default (one local-file write, approved
per call) · errors that are sentences, not stack traces · stdout reserved for the
protocol (audit logs go to stderr).
