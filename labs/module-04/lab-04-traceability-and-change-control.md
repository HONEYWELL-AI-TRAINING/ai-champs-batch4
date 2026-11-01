# Lab 04 — Traceability & Change Control

**Time:** ~30 min · **Surface:** Copilot Chat + terminal ·
**Prereq:** Lab 03 complete (feature built, validated, PR open)

## Objective

A requirement changes. Handle it the spec-driven way — **update `spec.md`
first**, then regenerate plan, tasks, and code from that single source of truth —
and do the *same* change prompt-only on a throwaway branch to feel the
difference. Close the traceability matrix.

## Why it matters for the enterprise

Requirements always change. The question is whether the change flows through a
controlled artifact or gets bolted onto the code and lost. Prompt-only, a spec
change means re-explaining the whole feature and hoping nothing regresses —
with no record of *why* the code now looks different. Spec-driven, the change is
a diff to `spec.md`, a regenerated task or two, and an updated test, with the
"why" captured forever.

## The change

> **New requirement:** a comment can be **deleted only within 5 minutes of being
> posted**. After that, `DELETE` returns `409 Conflict` with a body explaining
> the window has passed. (This is a real change: a new status code the current
> error contract doesn't have, a time-based rule, and a new acceptance
> criterion.)

---

## Part A — spec-driven change control

### Step 1 — Update the constitution if needed

The current constitution says "404 / 422 only, no other codes". This change
introduces `409`. That's a constitutional decision — make it explicitly:

```
/speckit.constitution

Amend principle 3 (error contract): CRUD endpoints use 404 for a missing
resource and 422 for a bad request body. 409 Conflict is permitted ONLY for a
valid request that violates a state/time rule (e.g. an edit window has closed),
with a body explaining the conflict.
```

Commit the amended constitution.

### Step 2 — Update the spec first

```
/speckit.specify

Amend specs/001-task-comments/spec.md: a comment may be deleted only within
5 minutes of its created_at. A DELETE after that window returns 409 with
{ "error": "deletion window (5 minutes) has passed" }. Add the requirement,
update the DELETE acceptance criteria, keep everything else unchanged.
```

Review the `spec.md` diff. There should be a new `REQ-xx`, a changed
`AC` for delete, and **nothing else touched**.

### Step 3 — Regenerate downstream

```
/speckit.plan     → update the design: where the 5-minute check lives
                    (service layer — it's a business rule, not DB access),
                    the 409 mapping in the router.
/speckit.tasks    → should produce a small delta: ~2 changed tasks
                    (service rule + tests), not a rewrite.
/speckit.analyze  → confirm spec/plan/tasks are consistent again.
```

### Step 4 — Implement the delta

```
/speckit.implement   (only the changed/new tasks)
```

Verify:

**macOS / Linux**

```bash
cd backend-python && pytest -q -k comment ; cd ..
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q -k comment ; cd ..
```

Add a test that posts a comment, back-dates its `created_at` past the window
(directly in the fixture), and asserts `409`.

### Step 5 — Re-port and re-validate

- Re-run the `port-endpoint` skill for the DELETE change on the .NET backend.
- `compare-responses.sh "/api/tasks/1/comments/1"` for the 409 case.
- Update `acceptance-checklist.md` with the new criterion.
- Update `usecase.md` (DELETE now can return 409).

### Step 6 — Record it

Fill the **Change log** table in `specs/001-task-comments/traceability.md`:

| Date | Spec change | Artifacts regenerated | Tasks changed | Tests changed |
|------|-------------|-----------------------|---------------|---------------|
| today | REQ-xx: 5-min delete window, 409 | constitution, spec, plan, tasks | T00x (service rule), T00y (tests) | +1 backend, +1 .NET |

Commit:

```bash
git add -A && git commit -m "Module 04 Lab 04: delete-window change via spec-driven change control"
```

---

## Part B — the same change, prompt-only

### Step 7 — Throwaway branch, no spec

Branch from the feature branch **as it was at the end of Lab 03** (before the
Part A change), so the comments feature exists but the spec-driven change does
not:

```bash
git checkout 001-task-comments
git checkout -b m04-promptonly-change <commit-at-end-of-lab-03>
```

New Copilot Chat, **do not** open or mention `spec.md` / `plan.md` / `tasks.md` /
`constitution.md` — work as if they don't exist. One prompt:

```
Change the task comments feature so a comment can only be deleted within
5 minutes of being created. After that, deleting it should fail with a 409.
Update the code and tests.
```

Let it work. Then answer, honestly, on a scratch note:

| Question | Spec-driven (Part A) | Prompt-only (Part B) |
|----------|---------------------|----------------------|
| Where is the "why" for this change recorded? | | |
| Did the `409` decision get checked against the error contract? | | |
| Were the other backends updated / flagged? | | |
| How would a reviewer trace this code to a requirement? | | |
| If the window changes to 10 min next week, what do you edit? | | |
| Iterations / time to a result you'd merge | | |

### Step 8 — Discard Part B

```bash
git checkout 001-task-comments && git branch -D m04-promptonly-change
```

It was only to feel the contrast. Part A is the real work.

---

## Step 9 — Close the traceability matrix

Back on the feature branch, complete every column of
`specs/001-task-comments/traceability.md`:

- Every `REQ` → task(s) → commit(s) → acceptance test(s) → ☑.
- No orphan code, no orphan requirements (the Lab 02 rules, re-checked).
- The change log records the delete-window amendment.

Push and update the PR. Run **Copilot code review** once more.

## Verify

- [ ] The `spec.md` diff for the change is minimal and came *before* the code.
- [ ] `constitution.md` was amended for the new status code.
- [ ] `/speckit.tasks` produced a small delta, not a rewrite.
- [ ] A test proves `409` after the window; `pytest` + ported backend green.
- [ ] `traceability.md` is fully filled, including the change log.
- [ ] You can state, in one sentence each, what prompt-only lost: the record,
      the contract check, the parity, the traceability.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `/speckit.specify` rewrites the whole spec | Tell it "amend only — produce a minimal diff for this one requirement". Revert and retry. |
| `/speckit.tasks` regenerates all tasks | That's a signal the plan change was too broad. Narrow the plan edit to the service rule + tests. |
| The 5-min check ends up in the repository | It's a business rule → service layer. Constitution principle 1. Move it. |
| Prompt-only version "seems fine" | Re-read the Step 7 table — "fine" code with no spec, no contract check, and no parity is exactly the failure mode the module is about. |

## Recap — Module 04 complete

The Task Board repo now carries, under `specs/001-task-comments/`:

```
spec.md                  # requirements, constraints, contracts, acceptance criteria (+ amendment)
plan.md                  # reviewed architecture (+ data-model.md, contracts/)
tasks.md                 # ordered, verifiable work units
traceability.md          # REQ → task → commit → test, + change log
acceptance-checklist.md  # every criterion, bound to a passing test
```

…plus `.specify/memory/constitution.md`, the implemented + ported feature, and
first-hand evidence of what change control buys you over prompt-only.

**Module 05** takes this same specification through the full SDLC — greenfield
and brownfield — including architecture analysis and change-impact review.
