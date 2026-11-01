# Lab 03 — Custom Chat Modes & Custom Agents

**Time:** ~20 min · **Surface:** VS Code (chat modes); Copilot coding agent (`.github/agents`) ·
**Prereq:** Lab 02 complete

## Objective

Build **scoped Copilot personas** for the Task Board: a *Test Author* mode that
can only touch test files, and an *API Reviewer* mode that is read-only and uses
a reasoning model. Then add a repo-level *custom agent* the Copilot coding agent
picks up.

## Why it matters for the enterprise

A general chat can do anything, which means it can also do the wrong thing —
edit production code when you wanted a review, use an expensive model for a
trivial task. A custom mode is a **guardrail**: it fixes the instructions, the
allowed tools, and the model for a category of work, so the safe path is the
default path. It is also how you standardize *review rigor* across a team.

## Background — modes vs agents

| Mechanism | File | Where it runs | Picks |
|-----------|------|---------------|-------|
| **Custom chat mode** | `.github/chatmodes/NAME.chatmode.md` | VS Code Copilot Chat (mode dropdown) | instructions + `tools` + `model` |
| **Custom agent** | `.github/agents/NAME.md` (or entries in `AGENTS.md`) | Copilot coding agent / CLI | instructions + tools, invoked by name |

The formats are converging. This lab does chat modes in detail (you can use them
immediately in the IDE) and adds one custom agent file for the coding agent used
in Lab 06.

---

## Step 1 — Create the folders

**macOS / Linux**

```bash
mkdir -p .github/chatmodes .github/agents
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force -Path .github\chatmodes, .github\agents | Out-Null
```

In VS Code you can also use Command Palette → **Chat: New Mode File**.

## Step 2 — *Test Author* chat mode

```md
<!-- .github/chatmodes/test-author.chatmode.md -->
---
description: Writes and runs tests for the Task Board. Does not modify source code.
tools: ['codebase', 'search', 'editFiles', 'runCommands', 'testFailure']
---
# Test Author mode

You write tests only. You may edit files matching
`**/*{test,Test,tests,Tests,_test}*` and nothing else. If a test reveals a bug
in source code, describe the bug and the fix but do NOT edit the source — hand
it back to me.

Follow `.github/instructions/tests.instructions.md`:
- Mirror the neighbouring test file's framework and style.
- Every endpoint: happy path + `404` + `422`.
- Use existing fixtures/fakes; never a real database.

Workflow for every request:
1. Find the existing test file for the code under test.
2. Add the missing cases.
3. Run the suite for that backend and report the summary.
4. If a test fails, decide: is it the test or the source? Fix the test; flag
   the source.
```

## Step 3 — *API Reviewer* chat mode (read-only, reasoning model)

```md
<!-- .github/chatmodes/api-reviewer.chatmode.md -->
---
description: Read-only reviewer. Checks changes against the Task Board contract and architecture.
tools: ['codebase', 'search', 'changes']
model: Claude Sonnet 5
---
# API Reviewer mode

You are a senior reviewer. You never edit files. You produce a review.

Check the current changes (or the code I point you at) against:
- `.github/copilot-instructions.md` — layer boundaries, schema ownership,
  error contract.
- `usecase.md` — the API contract table (methods, paths, status codes, bodies).
- Cross-backend consistency — would the same request return the same shape from
  the other two backends?

Output:
1. **Verdict** — approve / request changes.
2. **Blocking issues** — file:line, the rule broken, the minimal fix.
3. **Non-blocking suggestions** — clearly separated.
4. **Test gaps** — behaviour that changed with no matching test.

Be specific and short. No praise, no restating the diff.
```

> **Model names** vary by what your org has enabled. Use any strong reasoning
> model available in your model picker; if the exact name is rejected, remove
> the `model:` line and select it manually.

## Step 4 — A custom agent for the coding agent (used in Lab 06)

```md
<!-- .github/agents/endpoint-builder.md -->
---
name: endpoint-builder
description: Implements a single Task Board endpoint change end to end, with tests, following repo rules.
---
You implement one endpoint-level change per task, in ONE backend (the one the
issue names, or Python if unspecified).

Rules (from `.github/copilot-instructions.md`):
- Repository → Service → Controller layering. No SQL outside the repository.
- No schema changes unless the issue explicitly asks for one.
- Error contract: 404 missing id, 422 missing title / unknown status.
- Add tests in the same layer before you consider the work done. Run the
  backend's test command; the task is not complete until it passes.

Deliverable: a single focused commit + a PR description that lists the files
changed, the tests added, and the test-run output.
```

## Step 5 — Use the modes

1. Reload VS Code (**Developer: Reload Window**).
2. Open the Copilot Chat mode dropdown (top of the chat panel — it lists *Ask*,
   *Edit*, *Agent*, then your custom modes). Select **API Reviewer**.
3. Make a small change to a controller — e.g. in the open backend, add a stray
   bit of validation logic *in the controller* instead of the service.
4. Ask: `Review my current changes.` Confirm the reviewer flags the misplaced
   validation as a layer violation and does **not** offer to edit anything.
5. Switch to **Test Author**. Ask: `Add the missing 422 test for creating a task
   with an unknown status.` Confirm it edits only a test file and runs the suite:

   **macOS / Linux**

   ```bash
   cd backend-python && pytest -q -k status
   ```

   **Windows (PowerShell)**

   ```powershell
   cd backend-python ; pytest -q -k status
   ```

6. Revert the deliberate controller change.

## Step 6 — Commit

```bash
git add .github/chatmodes .github/agents && git commit -m "Add custom chat modes and coding agent"
```

## Verify

- [ ] Two `.chatmode.md` files and one `.github/agents/*.md` file exist.
- [ ] Both modes appear in the VS Code chat mode dropdown.
- [ ] *API Reviewer* refuses to edit files and produces a structured verdict.
- [ ] *Test Author* edits only test files.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Custom modes not in the dropdown | Reload the window; confirm `.chatmode.md` suffix and `.github/chatmodes/` location. |
| Mode still edits source files | The `tools` list is advisory in some builds — the instruction text ("you never edit files") is what enforces it, so keep it firm. |
| `model:` rejected | Remove the line and pick the model manually in the chat panel. |
| JetBrains user | Custom chat modes are VS Code-first; use the equivalent prompt files from Lab 02 in JetBrains for now. |

## Recap & carry-forward

You now have review and test personas that enforce the house rules by
construction. **Lab 04** packages reusable know-how as skills; **Lab 05** gives
Agent mode real external tools via MCP; **Lab 06** hands `endpoint-builder` to
the cloud coding agent.
