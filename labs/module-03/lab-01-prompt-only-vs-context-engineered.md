# Lab 01 — Prompt-Only vs Context-Engineered, Measured

**Time:** ~35 min · **Surface:** Copilot Chat (Agent mode) + terminal ·
**Prereq:** Module 03 [set-up](README.md#set-up--do-this-once-before-lab-01) done; database + your backend running

## Objective

Implement `GET /api/tasks/stats` **for real, twice** — once from a bare prompt
with no repository context, once with context you choose on purpose — and record
the difference on the [token worksheet](token-worksheet.md): quality, tokens,
iterations, time.

## Why it matters for the enterprise

"Context engineering is worth the effort" is an opinion until you have numbers: a
prompt-only pass that needed four iterations and still shipped the wrong keys,
versus a context-engineered pass that was right the first time for a little more
up-front context. Those numbers are the baseline every later module's cost
discussion refers back to.

## Background — a well-framed prompt in one minute

A prompt-only pass still needs a *decent* prompt, or the comparison isn't fair.
A decent prompt has four parts:

| Part | For the stats task |
|------|--------------------|
| **Frame** — one sentence, what exists when done | "Add a read-only endpoint that returns task counts by status." |
| **Role / instruction** — perspective + what to do | "As the backend maintainer, implement it and add a test." |
| **Constraints** — the limits that must hold | keys exactly `todo` / `in-progress` / `done`; query in the repository; no schema change |
| **Example** — anchor the shape | `{ "todo": 3, "in-progress": 2, "done": 1, "total": 6 }` |

The difference this lab measures: in **Pass A** you *type* the constraints from
memory (and usually miss some). In **Pass B** the constraints come from
**context you attach** — the repo's own files — so they're complete and correct
without you retyping them.

## Set-up — isolate the two passes

Branch off `module-03-context` for each pass:

```bash
git checkout module-03-context
git checkout -b m03-lab01-passA        # Pass A works here
```

Copy the worksheet:

**macOS / Linux**

```bash
cp ../module-03/token-worksheet.md worksheets/token-worksheet-$USER.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-03\token-worksheet.md worksheets\token-worksheet-$env:USERNAME.md
```

---

## Pass A — prompt-only

**Rules for this pass:** a **new empty chat**, Agent mode, **no `#` context, no
relevant files open, no reference to `copilot-instructions.md`**. To keep the
comparison honest, temporarily disable the repo instruction file:

**macOS / Linux**

```bash
mv .github/copilot-instructions.md .github/copilot-instructions.md.off
```

**Windows (PowerShell)**

```powershell
Rename-Item .github\copilot-instructions.md .github\copilot-instructions.md.off
```

### Step A1 — one prompt (framed, but no repo context)

```
As the maintainer of this backend, add a read-only GET /api/tasks/stats endpoint
that returns how many tasks are in each status plus a total, e.g.
{ "todo": 3, "in-progress": 2, "done": 1, "total": 6 }.
Implement it and add a test.
```

### Step A2 — iterate until you'd open a PR

Let the agent work. **Every follow-up you send** ("no, the keys should be…",
"move that query", "the test is failing") is **one iteration — tally it**. Stop
when the result is something you would actually submit.

### Step A3 — score Pass A

Run the backend tests:

**macOS / Linux**

```bash
cd backend-python && pytest -q ; cd ..
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q ; cd ..
```

Fill the **Pass A** column of the rubric and metrics tables. For "context sent",
use the IDE chat context gauge if shown, else `~<your prompt chars>/4` plus a
note that the agent also opened files itself. List every rubric item Pass A got
wrong (keys as `inProgress`, query in the router, missing `total`, no test…).

### Step A4 — reset

```bash
git checkout -- . ; git clean -fd backend-python frontend
git checkout module-03-context ; git checkout -b m03-lab01-passB
```

Restore the instruction file:

**macOS / Linux**

```bash
mv .github/copilot-instructions.md.off .github/copilot-instructions.md
```

**Windows (PowerShell)**

```powershell
Rename-Item .github\copilot-instructions.md.off .github\copilot-instructions.md
```

---

## Pass B — context-engineered

**Rules for this pass:** a new chat, Agent mode, and context you **choose on
purpose** — the minimum that makes the task unambiguous, not "add everything".

### Step B1 — assemble the context

In the chat input, use **Add Context** (or type `#`) to attach exactly these:

| Context | Why it's in | How to add |
|---------|-------------|-----------|
| `.github/copilot-instructions.md` | Layer rules, error contract, schema ownership | auto-included; or `#copilot-instructions.md` |
| Your backend's repository file (e.g. `repositories/task_repository.py`) | The pattern the count query must follow | `#task_repository.py` |
| The existing list handler (e.g. `routers/tasks.py`) | Error-mapping + response style to mirror | `#tasks.py` |
| The matching test file | The conventions the new test must match | `#test_tasks_api.py` |
| `usecase.md` — **the API-contract lines only** | The status enum and JSON shape | paste the ~6 relevant lines; don't attach the whole file |

Do **not** attach: the frontend, the other backends, the whole `usecase.md`, the
Module 02 skills. They're available; they're not relevant here.

### Step B2 — one prompt, same four parts, context does the rest

```
You are the maintainer of this backend. Implement GET /api/tasks/stats.

Returns:
{ "todo": 3, "in-progress": 2, "done": 1, "total": 6 }

Constraints (see the attached copilot-instructions.md):
- The GROUP BY / aggregation query goes in the repository layer only.
- Keys are exactly "todo", "in-progress", "done", plus "total".
- Mirror the error-mapping and response style of the attached list handler.
- No change to database/schema.sql.

Steps: 1) repository method  2) service method  3) router handler
4) tests in the attached test file (happy path + total-equals-sum check).
Run the tests and show me the diff.
```

### Step B3 — score Pass B

Run the tests (same commands as A3). Fill the **Pass B** columns. For "context
sent":

**macOS / Linux**

```bash
tools/estimate-tokens.sh .github/copilot-instructions.md backend-python/repositories/task_repository.py backend-python/routers/tasks.py backend-python/tests/test_tasks_api.py
```

**Windows (PowerShell)**

```powershell
.\tools\estimate-tokens.ps1 .github\copilot-instructions.md backend-python\repositories\task_repository.py backend-python\routers\tasks.py backend-python\tests\test_tasks_api.py
```

Add your prompt (~150 tokens) and the pasted contract lines (~80). That sum is
your **context budget** for this task.

### Step B4 — keep Pass B

```bash
git add -A && git commit -m "Add GET /api/tasks/stats (context-engineered)"
git checkout module-03-context && git merge --no-ff m03-lab01-passB
```

---

## Step 3 — Compare and reflect

Fill the **Notes** section of the worksheet:

- Pass A total rubric score vs Pass B (Pass B should be 12–14; Pass A often 6–9).
- Tokens: Pass B's *up-front* context is bigger, but add up Pass A's **iteration
  prompts + re-reads** — prompt-only usually costs *more* total tokens and more
  wall-clock time by the time it's correct.
- The last worksheet line: what is the **smallest** context that still gets Pass
  B's result? (Often: `copilot-instructions.md` + the repository file + the
  contract lines.) You test that hypothesis in Lab 02.

## Verify

- [ ] `worksheets/token-worksheet-<you>.md` is filled in for both passes.
- [ ] Pass B is committed; Pass A code was discarded.
- [ ] `.github/copilot-instructions.md` is restored (no `.off` file left behind).
- [ ] You can state the token and iteration difference in one sentence.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Pass A came out fine | The instruction file wasn't actually disabled, or a relevant file was open in the editor (the agent reads it). Re-check, redo. |
| Can't tell how many tokens were sent | Use the IDE chat context gauge if present; otherwise the `estimate-tokens` sum of attached files is a fair proxy. The *ratio* matters, not precision. |
| Left a `.off` file | `git status` shows it. Rename it back and delete the `.off`. |
| Pass B needed iterations too | Note which context was missing and add it — that *is* the lab working. |

## Recap & carry-forward

You have numbers. **Lab 02** turns "attach exactly these" into a repeatable
routine — select → compress → scope — and bottles it as a `/context-brief`
prompt and a `CONTEXT.md` the whole team reuses.
