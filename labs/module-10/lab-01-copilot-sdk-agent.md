# Lab 01 — Build a Code-Based Agent with the GitHub Copilot SDK

**Time:** ~45 min · **Surface:** terminal + editor (Python) ·
**Prereq:** `uv`, Python 3.11+ (uv fetches it), and a Copilot subscription **or** the offline mode below

Modules 07 and 09 used agents someone else built. Here you build one in code, see
exactly what runs, and put **controls around the loop**. Lab 02 then grounds this
same agent in your documents.

## Objective

Build a single-purpose agent with the **Copilot SDK** — instructions, one
read-only tool, an allow-list, a permission handler, a step cap and a trace — run
it, and read what it did and what it cost.

## Why it matters for the enterprise

An agent is *code that spends money and takes actions* (deck slide 16). The
SDK gives you the same runtime as Copilot CLI — the loop, tool calling, sessions —
so you don't write orchestration. What it doesn't give you is *judgement about
what this agent may do*. That part is yours, and it lives in a few dozen lines.

## Background

```
 your code ──▶ Copilot SDK ──JSON-RPC──▶ agent runtime (Copilot CLI) ──▶ models + your tools
 (this lab)    (library)                 runs the LOOP, tools, sessions      │
                                                  ▲                          ▼
                              your hooks / permission handler  ◀── "may I call get_build_status?"
```

The deck's pseudocode (slide 7) maps to the real SDK like this:

| Deck | Copilot SDK (Python, v1.0.x) |
|------|------------------------------|
| `create_agent(instructions, tools)` | `client.create_session(system_message=…, tools=[…], available_tools=[…], hooks=…, on_permission_request=…)` |
| `tool name / description / inputs / handler` | `@define_tool(description=…)` on an `async def f(params: PydanticModel)` |
| `agent.send(prompt)` | `await session.send_and_wait(prompt, timeout=…)` |
| "stop conditions" | `available_tools` (allow-list) · permission handler · `on_pre_tool_use` hook (your step cap) · `timeout` · `session.abort()` |
| "trace" | hooks + `session.on(...)` events (`assistant.usage` = one per model call) |

> **Verify against current docs.** The SDK is generally available but moves fast
> ([github/copilot-sdk](https://github.com/github/copilot-sdk)). This lab was built
> and run against `github-copilot-sdk` **1.0.22** (pinned in `uv.lock`). Hook
> keyword arguments are `snake_case`; the dicts you read and return are `camelCase`
> (`toolName`, `permissionDecision`) — copy them exactly, a typo is silent.

---

## Step 0 — Set up and check your environment (5 min)

```bash
cd labs/module-10/code-agent
uv sync
uv run python check_setup.py
```

`check_setup.py` starts the SDK's runtime (bundled for Python — fetched on first
use), reports whether you're signed in, and lists the models **your** account can
use. It makes **no model calls**, so it costs nothing.

Pick a model from the list and set it. The default in the code is `gpt-5-mini`;
if it isn't in your list, choose another:

**macOS / Linux**
```bash
export LAB_MODEL=gpt-5-mini
```
**Windows (PowerShell)**
```powershell
$env:LAB_MODEL = "gpt-5-mini"
```

> **No Copilot access?** Use **`--offline`** on every command in Labs 01–02. It
> runs the real SDK, runtime, tools, hooks and RAG against a tiny scripted local
> server (`mock_model.py`) instead of a language model. It proves the *plumbing* —
> not how a real model behaves, so the answer-quality lessons need a real run.

## Step 1 — The smallest agent (5 min)

*(Needs real Copilot. Offline? Read it, skip running it, and carry on to Step 2.)*

Create `hello.py`:

```python
import asyncio, os
from copilot import CopilotClient
from copilot.rpc import PermissionDecisionReject

async def main():
    async with CopilotClient() as client:                       # starts and stops the runtime
        async with await client.create_session(
            on_permission_request=lambda req, inv: PermissionDecisionReject(feedback="no tools in this agent"),
            model=os.environ.get("LAB_MODEL", "gpt-5-mini"),
            available_tools=[],                                  # offer the model NO tools
            system_message={"mode": "append", "content": "Answer in one sentence."},
        ) as session:
            reply = await session.send_and_wait("What is 2+2?", timeout=60)
            print(reply.data.content if reply else "(no assistant message)")

asyncio.run(main())
```

```bash
uv run python hello.py        # expect: 2 + 2 = 4.
```

Note three things you'll reuse: the client/session are **async context managers**;
`system_message` with `mode: "append"` adds your instructions to the runtime's own
prompt; and `available_tools=[]` is deliberate — see Step 4.

## Step 2 — Read the tool (5 min)

Open `agent/tools.py` and read `get_build_status` against the deck's four rules:

| Rule (slide 7) | Where it is in the code |
|----------------|-------------------------|
| **One tool, one job** | one lookup, nothing else |
| **Describe for the model** | `description="… Use when the user asks why a build failed or passed. id looks like b-1234."` |
| **Typed, validated inputs** | `BuildParams` (Pydantic) types the shape; the handler **re-checks** `b-\d{4}` and returns an error the model can read |
| **Small, structured output** | a 3-field JSON object, not a log dump |

It's read-only and has no side effects — the "day one" rule from slide 16. (This is
the same tool shape as Module 07's Build Insights server; a tool is a tool whether
it's an MCP server or a function in your code.)

## Step 3 — Run the agent and read the trace (8 min)

```bash
uv run python run_agent.py "Why did build b-1234 fail?"
# no Copilot? →  uv run python run_agent.py --offline "Why did build b-1234 fail?"
```

You'll see three things: the **answer**, the **trace** (one line per tool call:
tool, arguments, decision, size of the result), and the **usage**.

What I got on a real run (yours will differ in wording):

```text
ANSWER: Build b-1234 failed at the "unit-tests" step. … Want me to fetch the test logs/artifacts now?
TRACE :
   {'tool': 'get_build_status', 'args': {'build_id': 'b-1234'}, 'decision': 'allow', 'result_chars': 142}
USAGE : {'model_calls': 2, 'input_tokens': 4436, 'output_tokens': 503}
```

Answer these in `agent-notes.md`:

1. How many **model calls** did one question take, and why more than one? (Call 1: the model decides to use the tool. Call 2: it reads the result and answers — that is the **loop**, plan → act → observe → answer.)
2. How many **input tokens** for a one-line question? Where do they come from? (The runtime's own system prompt, your instructions, the tool schema and the history.) This is why "tool-heavy agents use far more of your budget than a single prompt" (slide 8).
3. The answer offers to *"fetch the test logs"*. Does the agent have a tool for that? **No.** That's the model offering something it can't do — an instructions problem (Step 5).

## Step 4 — Test the tool with bad input (3 min)

```bash
uv run python run_agent.py "Why did build b-99 fail?"
```

`b-99` doesn't match the pattern. The handler rejects it **inside the tool** and the
model reads the error and asks for a valid id — it doesn't make up a result. Check
the trace: the call is still `allow`ed (the *permission* layer approved the tool);
the *validation* layer rejected the **argument**. They're different controls.

## Step 5 — Debug in the deck's order: instructions → tools → model (8 min)

> "Most agent bugs trace back to one of the five parts being vague … Changing the
> model rarely fixes an unclear job." — slide 6

Open `agent/agent.py`. Make one change at a time and re-run Step 3's question; record
what changed in `agent-notes.md`:

1. **Instructions.** Delete `Say if unsure. Keep answers to three sentences.` from `BASE`. Is the answer longer? More confident? Put it back, then **add** `Never offer actions you have no tool for.` Does the "fetch the logs" offer disappear?
2. **Tools.** Change the tool `description` to just `"build info"`. Does the model still pick the tool for the right question? For a vaguer question such as `Is b-1235 ok?`
3. **Model.** Set `LAB_MODEL` to another model from `check_setup.py` and compare answer, tokens and speed. Did it fix anything the instructions didn't?

Rule of thumb you should now believe: fix them in that order.

## Step 6 — Controls around the loop (10 min)

Open `agent/guards.py` and `agent/agent.py` and map the deck's four control points
(slide 9) to the lines that implement them:

| Control point | Deck | Lab code |
|---------------|------|----------|
| **Before a tool call** | approve, deny or ask | `Guard.on_permission_request` (only *our* custom tools, by name) and `Guard.pre_tool_use` (allow-list + step cap) |
| **Inside the tool** | validate inputs | the regex in `get_build_status` |
| **After a tool call** | log, filter | `Guard.post_tool_use` — logs the **size** of the result, not its content |
| **Around the session** | step/time/cost limits | `max_tool_calls`, `send_and_wait(timeout=…)`, `abort()`, and `available_tools` |

Three facts to verify, not trust:

**a) `available_tools` removes the built-in tools.** By default the SDK exposes the
Copilot CLI's own tools (shell, file edit…), "similar to running the CLI with
`--allow-all`". Your agent should *not* have them. The test records which tools the
runtime offered the model:

```bash
uv run pytest -q tests/test_agent.py -k allow_list
```

**b) A step cap is something *you* implement.** The SDK has no `max_steps` knob
(the loop and its stopping decision belong to the runtime and the model). Our cap
counts tool calls in the pre-tool hook and, past the limit, denies the call and
aborts the session. Watch it stop a runaway:

```bash
uv run pytest -q tests/test_agent.py -k runaway
```

Then see it on the real model, with a cap of **zero** — the first tool call is
denied and the run ends instead of looping:

```bash
uv run python -c "
import asyncio
from agent.agent import ask, new_client
async def m():
    async with new_client() as c:
        a = await ask(c, 'Why did build b-1234 fail?', max_tool_calls=0, timeout=60)
        print(a.text); print(a.trace)
asyncio.run(m())"
# expect: (stopped: step cap of 0 tool calls reached) and a trace entry 'deny: step cap'
```

> **Pitfall worth knowing:** the first version of this cap `await`ed `session.abort()`
> *inside* the hook. The runtime stopped, but `send_and_wait` never saw the session go
> idle and waited out its whole timeout. The fix is in `guards.py`: schedule the abort
> as a task so the hook can return first.

**c) Cost is observable, not capped.** The `assistant.usage` event fires per model
call (that's your `USAGE` line). The SDK also has an *experimental* soft cap,
`session_limits={"max_ai_credits": N}`, "checked after model calls return" — one
response can overshoot it. For anything unattended, log usage **and** set limits.

## Step 7 — Run the automated checks (3 min)

```bash
uv run pytest -q            # 16 passed (offline: no Copilot usage)
```

They drive the **real SDK and runtime** against the scripted model, so you can
re-run them after any change to tools, guards or instructions without spending usage.
Add one test of your own — for example that `max_tool_calls=1` allows exactly one call.

## Verify

- [ ] `hello.py` answers; `check_setup.py` showed you signed in (or you're using `--offline`).
- [ ] `run_agent.py` printed an answer, a trace with `get_build_status`, and a usage line with **2 model calls**.
- [ ] `b-99` was rejected by the **tool**, and the agent asked for a valid id instead of inventing a status.
- [ ] In `agent-notes.md`: tokens per question, the unsupported "fetch logs" offer, and what each Step 5 change did.
- [ ] You can name the four control points and the code that implements each — and say which one the SDK does **not** give you built in (a step cap).
- [ ] `pytest` passes, including your added test.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `check_setup.py` says not authenticated | Sign in with the Copilot CLI / your GitHub account, or set `COPILOT_GITHUB_TOKEN` / `GH_TOKEN`; or use `--offline` |
| Model not found / unsupported | Run `check_setup.py`, pick a listed model, set `LAB_MODEL` |
| First run is slow | The runtime is downloaded on first use (`uv run python -m copilot download-runtime` does it up front) |
| `send_and_wait` times out | Raise `timeout`; check the trace for a denied tool the model keeps retrying |
| Hook seems ignored | Dict keys must be exact `camelCase` (`toolName`, `permissionDecision`); keyword names `snake_case` |
| The agent offers things it can't do | Instructions: say what it must *not* offer (Step 5.1) |
| Org/managed policy blocks `approve_all` | Why this lab uses its own handler; keep it |
| Corporate proxy / no network | Use `--offline`; or ask your admin about BYOK |

## Recap & carry-forward

- Agent = **instructions + model + session + tools**, plus hooks and permissions. Debug in that order.
- The loop is the runtime's; **the limits are yours** — allow-list, approval, time, and a step cap you write.
- Every model call has a cost you can observe; a tiny question can cost thousands of input tokens.
- **Lab 02** adds one more tool — `search_docs` — and measures whether grounding actually helps.
