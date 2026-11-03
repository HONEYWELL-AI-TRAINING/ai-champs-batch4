# Lab 04 — Your First Custom MCP Server (FastMCP)

**Time:** ~30 min · **Surface:** terminal + MCP Inspector ·
**Prereq:** `uv` and Node.js (`npx`) installed. Labs 01–03 are not required.

Labs 04–06 are the **custom-server track** of Module 07 (deck slides 12–16:
*Building Your Own*, *A Minimal Server*, *Lab 2: Build, Wire, Govern*). They use
the code in [`custom-mcp-server/`](custom-mcp-server/). Labs 01–03 (Jira, GitHub
and Playwright MCP servers) are independent and can be done before or after —
but they make a good warm-up, because they show what a finished server feels like
from the host side.

## Objective

Write a one-tool MCP server with FastMCP, run it, and prove it works in the
**MCP Inspector** — including with bad input — before any agent touches it.

## Why it matters for the enterprise

An approved server for your CI, test lab or docs often doesn't exist. A small
server you own and can review is cheaper and safer than a broad one you can't.
The Inspector is how you check it **without a model in the loop**, so a failure
is the server's fault or it isn't.

## Background — what you're building

```
 Inspector (client)  ──JSON-RPC over stdio──▶  server_minimal.py  ──▶  (stub data)
                                                  └─ tool: get_build_status(build_id)
```

Rule of thumb from the deck: *if the model should decide to do it, make it a
tool.* Here the model decides to look up a build, so it's a tool.

---

## Step 1 — Install

```bash
cd labs/module-07/custom-mcp-server
uv sync
uv run fastmcp --version      # expect 4.x
```

## Step 2 — Read the server

Open `server_minimal.py`. It is the deck's twenty-line example, complete:

```python
from fastmcp import FastMCP

mcp = FastMCP("Build Tools")

@mcp.tool
def get_build_status(build_id: str) -> dict:
    """Return the status and failing step of a CI build. Read-only.

    build_id looks like 'b-1234'.
    """
    if not build_id.startswith("b-"):
        raise ValueError("invalid build id: expected something like 'b-1234'")
    return {"id": build_id, "status": "failed", "step": "unit-tests"}

if __name__ == "__main__":
    mcp.run()  # stdio by default
```

Answer these before running anything:

1. Where does the **tool name** come from? Where does the model's **description** come from?
2. Where does the **input schema** come from?
3. What does the client see if the id is invalid?

(Answers: function name · docstring · the type hints · the `ValueError` message.)

## Step 3 — Run it in the Inspector

```bash
uv run fastmcp dev inspector server_minimal.py
```

A browser tab opens on the Inspector. **Connect**, open the **Tools** tab,
list tools, and select `get_build_status`.

> The terminal prints an Inspector URL containing a session token. Treat it
> like a password; don't paste it anywhere.

## Step 4 — Call it three ways

| Input | Expected |
|-------|----------|
| `b-1234` | `{"id": "b-1234", "status": "failed", "step": "unit-tests"}` |
| `1234` | **Error** with your message: "invalid build id…" |
| *(empty)* | **Error** — either "required" or your "invalid build id" message, depending on how the Inspector sends an empty field |

Note what the failure looks like. That text goes into the model's context, so
it must be a clear sentence — never a stack trace, never a secret.

## Step 5 — Make one change and re-test

Add a second validation: reject ids longer than 10 characters. Restart the
Inspector session (stop with `Ctrl+C`, re-run Step 3) and prove the new rule
with `b-123456789`.

## Step 6 — Same checks without the browser

```bash
npx -y @modelcontextprotocol/inspector --cli uv run --quiet python server_minimal.py \
  --method tools/call --tool-name get_build_status --tool-arg build_id=b-1234
```

Re-run with `--tool-arg build_id=oops` and confirm `"isError": true`. This CLI
form is what you'd put in a script or CI job.

## Verify

- [ ] You can state where the tool's name, description and schema come from.
- [ ] A valid call returns the expected object.
- [ ] An invalid id returns a **clear error**, and the server keeps running.
- [ ] You ran the same call through both the Inspector UI and `--cli`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `fastmcp dev server_minimal.py` fails | In FastMCP 4.x the command is `fastmcp dev inspector server_minimal.py` |
| Browser doesn't open | Open the `http://127.0.0.1:6274?…` URL from the terminal manually |
| Inspector connects then drops | Something printed to **stdout**. On stdio, stdout is the protocol; use `logging` to stderr, never `print` |
| `npx` not found | Install Node.js; `node --version` must work in the same terminal |

## Recap & carry-forward

- A tool = function + docstring + type hints. The docstring **is** the instruction to the model.
- You tested without an agent. **Lab 05** grows this into a real server with typed, bounded inputs, a resource, and a prompt; **Lab 06** wires it into Copilot and governs it.
