# Lab 05 — Tools, Resources & Prompts: Design a Small, Safe Server

**Time:** ~40 min · **Surface:** editor + MCP Inspector + `pytest` ·
**Prereq:** [Lab 04](lab-04-first-fastmcp-server.md)

## Objective

Grow the minimal server into **Build Insights**: three read-only tools, one
guarded write (a local draft), a resource, and a prompt — each designed against
the deck's five tool-design principles — and test it in the Inspector and with
`pytest`.

## Why it matters for the enterprise

The anti-pattern from the deck is a single `run_query(sql)` / `run_command(cmd)`
tool: it hands the model your whole system. Narrow, typed, bounded tools turn
"what can the agent do?" into a list a reviewer can read in a minute.

## Background — pick the right building block

| Block | Controlled by | Use it for | In this server |
|-------|---------------|------------|----------------|
| **Tool** | the model | actions / lookups it should decide to run | `get_build_status`, `list_recent_builds`, `get_test_failures`, `draft_followup_issue` |
| **Resource** | the application | context to attach | `docs://index`, `docs://runbooks/{name}` |
| **Prompt** | the user | a reusable, human-triggered template | `explain_build_failure` |

---

## Step 1 — Design on paper first (10 min)

Before code, fill this table in your notes. The reference answer is below —
don't scroll yet.

| Tool | Job (one sentence) | Inputs (type + limits) | Output (what, how big) | Read / write |
|------|--------------------|------------------------|------------------------|--------------|
| | | | | |

<details><summary>Reference design</summary>

| Tool | Job | Inputs | Output | R/W |
|------|-----|--------|--------|-----|
| `get_build_status` | status of one build | `build_id` matches `^b-\d{4}$` | one small object | read |
| `list_recent_builds` | which builds exist | `status` ∈ {all, passed, failed, running}; `limit` 1–20 | ≤ 20 `{id, branch, status}` rows | read |
| `get_test_failures` | why a build failed | `build_id` | ≤ 10 failures × ≤ 300 chars | read |
| `draft_followup_issue` | save a draft for human review | `build_id`, `title` 5–120 chars, `summary` 10–2000 chars | `{saved, posted: false}` | **write (local file only)** |

</details>

## Step 2 — Separate the data layer

Open `data.py`. All access to the "system of record" (mock CI data here) lives
in this one module. Tools stay thin; a real server would call the CI API only
from here, which makes review and credential handling easy.

> Notice build `b-1003` in `data.py`: one failure message contains
> `IGNORE PREVIOUS INSTRUCTIONS…`. It's a planted prompt-injection string for
> Lab 06. Real CI output is untrusted input too.

## Step 3 — Typed, validated inputs

Starting from `server_minimal.py`, the reference `server.py` replaces the
hand-written `startswith` check with a **declared** constraint:

```python
BuildId = Annotated[str, Field(pattern=r"^b-\d{4}$", description="Build id, e.g. 'b-1002'")]

@mcp.tool(annotations={"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False})
def get_build_status(build_id: BuildId) -> dict:
    """Return status, branch, commit and failing step for one CI build.

    Read-only. Use this before get_test_failures. build_id looks like 'b-1002'.
    """
```

Why this is better: the pattern appears in the **schema the model sees**, so it
usually gets the argument right first time, and the framework rejects bad input
before your code runs. `readOnlyHint` lets the host treat this tool as safe.

Do it: copy the `BuildId` alias and `get_build_status` from `server.py` into
your own copy (`server_lab.py` — start from `server_minimal.py`) and re-test
`b-12`.

## Step 4 — Bounded outputs and enums

Add `list_recent_builds` and `get_test_failures`. Two things to copy deliberately:

```python
status: Annotated[Literal["all", "passed", "failed", "running"], Field(description="Filter by build status")] = "all",
limit:  Annotated[int, Field(ge=1, le=20, description="Max builds to return")] = 5,
```

```python
failures[:MAX_FAILURES]  and  f["message"][:MAX_MESSAGE_CHARS]
```

`Literal` gives the model a closed list of choices; `ge`/`le` and the slices
keep the result small, so a noisy build can't flood the model's context.

## Step 5 — One guarded write

`draft_followup_issue` is the only write. Read it in `server.py` and find the
four safeguards:

1. `readOnlyHint: False` — the host can see it is not a read.
2. Docstring says it **only drafts** and posts nothing.
3. Writes to a fixed folder; filename comes from the regex-validated `build_id`, never from free text.
4. Returns `posted: false` so the model can't claim it filed an issue.

## Step 6 — A resource and a prompt

```python
@mcp.resource("docs://runbooks/{name}", mime_type="text/markdown")
def read_runbook(name: str) -> str:
    if not re.fullmatch(r"[a-z0-9-]{1,40}", name):   # allow-list, not "strip ../"
        raise ResourceError("Invalid runbook name.")
    ...

@mcp.prompt
def explain_build_failure(build_id: str) -> str:
    """Ask the agent to explain why a build failed and propose next steps."""
    return "Investigate CI build ... Do NOT call draft_followup_issue until I approve ..."
```

The resource is *context the application attaches*; the prompt is *something a
person chooses*. The prompt also encodes a human checkpoint ("do not draft until
I approve").

## Step 7 — Test in the Inspector

```bash
uv run fastmcp dev inspector server.py
```

Work through the **check matrix** in [TESTING.md §2a](custom-mcp-server/TESTING.md#2a-inspector-ui-interactive)
(11 checks: valid, invalid, missing, unknown, limits, truncation, write, resource,
name guard). Record results in [`test-notes.md`](custom-mcp-server/test-notes.md).

Also confirm the schema the model sees for each tool: open the tool in the
Inspector and read the description and schema as if you were the model. Would
you pick the right tool from the description alone?

## Step 8 — Lock it in with automated tests

```bash
uv run pytest -q          # 14 passed
```

Open `tests/test_server.py`. Each Inspector check is a test, using FastMCP's
in-memory `Client(mcp)` — no subprocess, no browser. **Add one test of your
own** for a bug or edge case you found in Step 7.

## Verify

- [ ] Your design table matches the reference (or you can justify the difference).
- [ ] Inspector: all 11 checks pass; every failure is a clear sentence, no stack trace.
- [ ] `pytest` passes, including your added test.
- [ ] You can name the one write tool and its four safeguards.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `Import "fastmcp" could not be resolved` in the editor | Select the interpreter `custom-mcp-server/.venv` |
| Tool result shows `{"result": [...]}` for list returns | Expected: MCP wraps non-object results; clients unwrap it |
| Validation errors mention `errors.pydantic.dev` | Expected; they come from Pydantic. The sentence before the link is the part to read |
| Test hangs | Make sure a stdio server from an earlier step isn't being reused; tests use the in-memory client only |

## Recap & carry-forward

- One tool, one job; describe it for the model; type and bound every input and output; read-only unless a write is essential.
- Tests that mirror your Inspector checks stop regressions.
- **Lab 06** registers this server in Copilot, observes approvals and an injection attempt, and writes the governance record.
