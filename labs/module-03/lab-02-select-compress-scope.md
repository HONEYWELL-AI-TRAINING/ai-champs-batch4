# Lab 02 — Engineer the Context: Select → Compress → Scope

**Time:** ~35 min · **Surface:** VS Code context controls + a new prompt file ·
**Prereq:** Lab 01 complete (you have a filled token worksheet and Pass B on `module-03-context`)

## Objective

Take the context pile from Lab 01 Pass B and run it through the three moves that
make context *cheap and sharp*: **select** the few sources that matter,
**compress** them to the lines that bind, **scope** them to this one task. Then
bottle the routine as `.github/prompts/context-brief.prompt.md` (`/context-brief`)
and write `CONTEXT.md` so the next person doesn't re-derive any of it.

## Why it matters for the enterprise

The model has a finite attention budget, and every irrelevant file you attach
spends it — on *every* turn. A sharp 800-token context beats a vague
8,000-token one at a tenth of the cost. This lab turns that from a lucky prompt
into a team habit with an artifact behind it.

## Background — the three moves

| Move | Question | Rule of thumb |
|------|----------|---------------|
| **Select** | Which sources does this task actually need? | Keep a file only if you can name a bug it prevents that nothing else catches. |
| **Compress** | What in those sources is redundant? | Summarise a spec to the lines that bind; reference a file, don't paste it; one example, not five. Put the most decision-relevant lines first — truncation eats the bottom. |
| **Scope** | What is *this* task, and only this task? | State non-goals. New chat per task. Don't carry the last task's context. |

---

## Step 1 — Select: build a context manifest

Create it:

```md
<!-- worksheets/context-manifest.md -->
# Context manifest — GET /api/tasks/stats

## Candidates (everything available)
| # | Source | Path / handle | Needed for THIS task? | Why / why not |
|---|--------|---------------|:--------------------:|---------------|
| 1 | Repo rules | `.github/copilot-instructions.md` | | |
| 2 | Repository layer | `backend-<x>/repositories/…` | | |
| 3 | Service layer | `backend-<x>/services/…` | | |
| 4 | Router (list handler) | `backend-<x>/routers/…` | | |
| 5 | Backend tests | `backend-<x>/tests/…` | | |
| 6 | API contract | `usecase.md` §API contract (status enum, shape) | | |
| 7 | DB schema | `database/schema.sql` | | |
| 8 | Frontend | `frontend/src/…` | | |
| 9 | Other backends | `backend-<y>/`, `backend-<z>/` | | |
| 10 | Issue history | `@github` — issues/PRs mentioning "stats" | | |

## Selected (in the order you'd attach them)
1.
2.
3.

## Rejected, and why
-
```

For each candidate apply the **select test**: *"If I remove this, could Copilot
get the task wrong in a way the other context wouldn't catch?"* If no → reject.

Expected outcome for `GET /api/tasks/stats`:

- **Select:** repo rules (1), repository layer (2), the list handler (4) for
  style, the contract lines (6). Maybe the test file (5).
- **Reject:** service layer (thin pass-through — 2 already shows the pattern),
  schema (7 — no schema change), frontend (8 — no UI), other backends (9 —
  parity is a later *check*, not context), issue history (10 — nothing relevant).

Fill the "why" column — the reasoning is the transferable skill. The selected
list should be **3–5 items, not 10**.

> **Tip — use `#codebase` as a selection assistant.** When you don't know which
> files matter: `#codebase Which files would I change to add GET /api/tasks/stats
> to the Python backend, and which file is the best pattern to copy? Paths only.`
> Verify each path, then add the good ones to your manifest as explicit `#file`
> attachments. `#codebase` is good for discovery, worse for precision.

## Step 2 — Compress: write the brief

The selected files are still big. Write the actual text you'd paste instead:

```md
<!-- worksheets/context-brief-stats.md -->
# Context brief — GET /api/tasks/stats

## Rules (from .github/copilot-instructions.md — only what binds THIS task)
- Layers: Controller/Router → Service → Repository. The GROUP BY lives in the
  repository. No SQL in the router or service.
- Error contract: 404 missing id, 422 bad request body. Don't invent codes.
  (This endpoint has no error cases beyond a malformed request.)
- Schema owned only by database/schema.sql — no migration, no create_all.

## Contract (from usecase.md §API contract)
- status ∈ { "todo", "in-progress", "done" } — literal strings, hyphen included.
- GET /api/tasks/stats → 200
  { "todo": <int>, "in-progress": <int>, "done": <int>, "total": <int> }
- total == todo + in-progress + done.

## Pattern to copy
repositories/task_repository.py → follow `list_tasks`; add `count_by_status()`
returning a dict keyed by the status string.

## Test
tests/test_tasks_api.py → one test: seed 3 tasks across 2 statuses, GET the
endpoint, assert the counts and total == sum. Use the existing client fixture.

## Non-goals
No frontend change. No change to GET /api/tasks. No new columns.
```

Measure the compression:

**macOS / Linux**

```bash
tools/estimate-tokens.sh .github/copilot-instructions.md usecase.md backend-python/routers/tasks.py backend-python/tests/test_tasks_api.py
tools/estimate-tokens.sh worksheets/context-brief-stats.md
```

**Windows (PowerShell)**

```powershell
.\tools\estimate-tokens.ps1 .github\copilot-instructions.md usecase.md backend-python\routers\tasks.py backend-python\tests\test_tasks_api.py
.\tools\estimate-tokens.ps1 worksheets\context-brief-stats.md
```

Expect the brief to be **5–20×** smaller than the raw sources.

## Step 3 — Scope: prove the compressed brief still works

Fresh chat, Agent mode, on a throwaway branch:

```bash
git checkout module-03-context && git checkout -b m03-lab02-brieftest
```

Attach **only** `worksheets/context-brief-stats.md` (instruction file still
active, nothing else) and prompt:

```
Implement GET /api/tasks/stats in the Python backend following the attached
context brief exactly. State any non-goal you would touch, then stop. Run the
tests and show the diff.
```

Compare the result to Lab 01 Pass B on the worksheet rubric. If it matches, the
brief captured what mattered. If it missed something, add that one line to the
brief — it was load-bearing. Then discard the branch:

```bash
git checkout module-03-context && git branch -D m03-lab02-brieftest
```

## Step 4 — Bottle it as `/context-brief`

```md
<!-- .github/prompts/context-brief.prompt.md -->
---
description: Build a compressed, layered, task-scoped context brief before implementing a change
mode: ask
---
I am about to implement: ${input:task:one sentence — what should exist when done}

Produce a **context brief** for this task and nothing else, in this structure:

## Rules
The 3–6 lines of `.github/copilot-instructions.md` that actually bind this task.
Quote them; don't summarise vaguely.

## Contract
The exact API shape, field names, types, and status codes involved — from
`usecase.md`. 6 lines max.

## Pattern to copy
The single best existing file/function to mirror: path + one line on what to take.

## Test
The one test file to touch and the 1–2 cases to add.

## Non-goals
What this task must NOT change (other endpoints, the frontend, the schema…).

Rules for the brief:
- Layer it in the order above (rules first — they survive truncation).
- Compress: reference files, don't paste them; one example, not many.
- Scope: if it isn't needed for THIS task, leave it out and list it under Non-goals.
- Total brief ≤ 400 tokens. If it won't fit, the task is too big — tell me to split it.
```

Run `/context-brief` with task `add ?assignee= filtering to GET /api/tasks/stats`,
sanity-check the brief it produces, then discard it (a demo).

## Step 5 — Write `CONTEXT.md` (the team habit)

```md
<!-- CONTEXT.md -->
# Working with AI context in this repo

## Per task
1. Run `/context-brief` (`.github/prompts/context-brief.prompt.md`).
2. Attach only its output. Add more context only if the brief-only run fails.

## What's usually enough
- `.github/copilot-instructions.md` (auto-included)
- The one repository/service/router file that is the pattern for the change
- The ~6 contract lines from `usecase.md` that apply
- The one test file you'll touch

## Leave out unless the task needs it
- The frontend for backend-only tasks (and vice versa)
- The other two backends — parity is checked with the `port-endpoint` skill, not
  carried as context
- Whole files when a `#selection` will do
- `database/schema.sql` unless the task changes the schema

## Session hygiene
- New chat when the task changes — don't carry the last task's context.
- Don't re-attach a file already discussed — reference it.
- Reach for a large-context model only after a tight brief has failed.
```

> **Optional — a shared Copilot Space.** If your org has Copilot
> Enterprise/Business, create a **`TaskBoard Context`** Space
> (github.com/copilot/spaces) with the repo, `usecase.md`,
> `database/schema.sql`, `.github/copilot-instructions.md`, and a short
> instruction block. It's `CONTEXT.md` as a reusable, shareable context so
> nobody re-attaches the same files. Not required to finish this lab.

## Step 6 — Commit

```bash
git add .github/prompts/context-brief.prompt.md worksheets/context-manifest.md worksheets/context-brief-stats.md CONTEXT.md
git commit -m "Module 03 Lab 02: context manifest + /context-brief prompt + CONTEXT.md"
git push
```

Optionally open a PR merging `module-03-context` into `main` so `CONTEXT.md`,
`context-brief.prompt.md`, and the token helper are on the default branch for
Module 04.

## Verify

- [ ] `worksheets/context-manifest.md` rates every candidate with a reason; the
      selected list is 3–5 items.
- [ ] `worksheets/context-brief-stats.md` is measurably smaller (5–20×) than the
      raw sources.
- [ ] The brief-only run reproduces Lab 01 Pass B's rubric score.
- [ ] `.github/prompts/context-brief.prompt.md` runs as `/context-brief` and
      enforces the ≤400-token / "split it" rule.
- [ ] `CONTEXT.md` is committed.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Manifest feels arbitrary | Re-apply the select test literally, one row at a time. If you can't name a failure the file prevents, reject it. |
| Brief-only result is worse than Pass B | A load-bearing line was compressed away — diff the brief against the raw sources, restore that line, note what it was. |
| `/context-brief` output is still huge | Tighten the "≤ 400 tokens" and "reference, don't paste" rules; re-run. |
| `#codebase` / `@workspace` not recognised | Newer VS Code uses `#codebase`; older uses `@workspace`. Agent mode also searches implicitly. |
| No Spaces option | Needs Copilot Enterprise/Business + org enablement. The `CONTEXT.md` + `/context-brief` combo is the fallback and is enough. |

## Recap — Module 03 complete

You added to the Task Board repo:

```
labs/module-01/
├── .github/prompts/context-brief.prompt.md   # Lab 02 — /context-brief
├── CONTEXT.md                                 # Lab 02 — repo context conventions
├── tools/estimate-tokens.{sh,ps1}             # set-up — rough token counter
└── worksheets/                                # token worksheet, manifest, brief
```

…and a measured baseline (the token worksheet) for every later module's cost
discussion.

**Module 04** builds specifications on exactly this discipline: a spec is a
deliberately selected, compressed, scoped context artifact — and the
`/context-brief` habit is the warm-up for writing one.
