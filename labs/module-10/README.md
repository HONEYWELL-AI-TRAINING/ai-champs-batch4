# Module 10 — Code-Based Agents (Copilot SDK) & a Simple RAG Flow (Hands-On Labs)

Companion labs for the Module 10 deck
([`presentations/Module10_Code_Agents_Copilot_SDK_RAG.pdf`](../../presentations/Module10_Code_Agents_Copilot_SDK_RAG.pdf))
and the background in [`guides/module-10-code-agents-copilot-sdk-simple-rag.md`](../../guides/module-10-code-agents-copilot-sdk-simple-rag.md).
Modules 07 and 09 used agents someone else built; here you **build one in code**, then **ground it in your own documents**.

One agent, built in layers — *tools first, then the loop, then your knowledge*:

| Lab | Focus | Time | You produce |
|-----|-------|------|-------------|
| [01](lab-01-copilot-sdk-agent.md) | A single-purpose agent with the **Copilot SDK**: instructions, one read-only tool, allow-list, permission handler, step cap, trace and usage | ~45 min | `hello.py`, `agent-notes.md` |
| [02](lab-02-simple-rag-pipeline.md) | The **RAG pipeline** end to end — index, retrieve, ground — plugged in as a tool, then measured grounded vs ungrounded | ~55 min | `rag-notes.md`, `baseline.md`, `grounded.md`, `comparison.md` |

Deck mapping: Lab 01 = slides 4–10 (chat → agent → loop → controls); Lab 02 = slides 11–15 (the
deck's *Lab: Build the Agent, Then Ground It*, whose files `agent/`, `docs/`, `baseline.md`,
`grounded.md`, `comparison.md` are exactly what you'll have). About **100 minutes** in total; the deck
budgets 35 min for its lab, so treat Lab 02 as the extended version.

## The code — [`code-agent/`](code-agent/)

| File | Role |
|------|------|
| `check_setup.py` | Preflight: runtime, sign-in, available models. **No model calls, no cost.** |
| `agent/tools.py` | `get_build_status` (read-only lookup) and `search_docs` (retrieval as a tool) |
| `agent/guards.py` | Controls around the loop: allow-list, permission handler, step cap, trace |
| `agent/agent.py` | One session = instructions + tools + guards; `ask()` runs a question and returns answer, trace, usage |
| `agent/rag.py` | The pipeline: `load` → `chunk` → `embed` → `Index` (store) → `search` |
| `docs/` | Three sample runbooks/policies — **all values invented** |
| `run_agent.py` | Ask one question (optionally `--docs docs`, `--strict`) |
| `rag_cli.py`, `eval_retrieval.py` | See and measure retrieval **without any model** |
| `run_lab.py` | Five questions, ungrounded vs grounded → the three `.md` outputs |
| `mock_model.py` | Scripted OpenAI-compatible server for `--offline` runs (not a language model) |
| `tests/` | 16 tests: RAG stages alone, plus the agent through the **real SDK runtime** against the scripted model |

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) — it installs Python 3.11+ for you.
- **GitHub Copilot access** for the real runs (a Copilot subscription, or BYOK — your own provider key; key-based auth only). The SDK bundles the runtime for Python; no separate CLI install.
- **No access?** Every command that talks to a model accepts **`--offline`**: the real SDK, runtime, tools, hooks and RAG, with a scripted server standing in for the model. It proves the plumbing, not answer quality.
- Org policy: ask your admin whether SDK / agent usage is permitted for your account before using work credentials.

```bash
cd labs/module-10/code-agent
uv sync
uv run python check_setup.py      # signed in? which models can I use?
uv run pytest -q                  # 16 passed — offline, free
```

## Cost and non-determinism — read this once

- The SDK counts toward your Copilot **usage allowance**, like the Copilot CLI. A one-line question took ~4,400 input tokens in my run (the runtime's own prompt dominates); the full Lab 02 comparison (10 sessions) took ~32,000 input and ~7,000 output tokens on `gpt-5-mini`.
- Model answers **vary between runs and models**. Numbers and answers quoted in the labs are from real runs on `gpt-5-mini` and are examples, not promises. Retrieval results (`rag_cli.py`, `eval_retrieval.py`) are deterministic and will match exactly.
- The model name in the code is a default (`gpt-5-mini`); available models depend on your account. Set `LAB_MODEL` after running `check_setup.py`.

## Platform conventions

Commands are identical on macOS, Linux and Windows (PowerShell) except setting an environment variable:
`export LAB_MODEL=…` (bash/zsh) vs `$env:LAB_MODEL = "…"` (PowerShell).

## Ground rules (same as Modules 07–09)

- One narrow job, a few **read-only** tools, a **human** who reads the result.
- Narrow the tool surface explicitly: by default the SDK exposes the CLI's own tools (shell, file edits); `available_tools=[…]` hides them.
- **Set limits** before running anything unattended; **log** every tool call and the usage.
- Tool results — and retrieved documents — are **untrusted input**.

## What's next

**Module 11** traces what this agent does and costs (Agent Prism) — the `trace` and `usage` the labs print are the raw material.
