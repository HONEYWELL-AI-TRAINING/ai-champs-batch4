# Lab 03 — Brownfield: Minimal-Change Implementation, Regression Protection & the Comparison

**Time:** ~60 min · **Surface:** Copilot Chat + terminal ·
**Prereq:** Lab 02 complete (archaeology, change-impact, spec, plan, tasks)

## Objective

Implement soft-delete with the **minimal-change strategy** — stay inside the
blast radius, follow existing patterns, run the **full** pre-existing suite
before and after. Then produce the regression report and the greenfield-vs-
brownfield comparison that closes the module.

## Why it matters for the enterprise

The measure of a brownfield change is not just "the feature works" — it's "the
feature works **and every pre-existing test still passes**". The minimal-change
strategy plus before/after regression runs is what lets a team move quickly on
old code without the "what did that break?" dread.

## Step 1 — Snapshot the suite BEFORE

**macOS / Linux**

```bash
{ cd backend-python && pytest -q ; cd ../frontend && npm test -- --run ; cd .. ; } 2>&1 | tee /tmp/suite-before.txt
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q *>&1 | Tee-Object $env:TEMP\suite-before.txt ; cd ..
cd frontend ; npm test -- --run *>&1 | Tee-Object -Append $env:TEMP\suite-before.txt ; cd ..
```

Record the counts (e.g. `pytest 19 passed`, `vitest 12 passed`,
`dotnet 14 passed`) at the top of a new file:

```md
<!-- specs/002-task-soft-delete/regression-report.md -->
# Regression Report — soft-delete

## Baseline (before the change)
- backend-python: __ passed
- frontend: __ passed
- backend-<ported>: __ passed
- Command(s): ...
- Date: 2026-__-__

## Intentionally changed tests (with justification)
| Test | Old assertion | New assertion | Why the change is correct (spec ref) |
|------|---------------|---------------|--------------------------------------|

## After the change
- backend-python: __ passed
- frontend: __ passed
- backend-<ported>: __ passed
- New regression tests added: ...
- Delta vs baseline explained: ...
```

## Step 2 — Add regression tests FIRST (task 1 from `tasks.md`)

Before changing any behaviour, pin what must not move. In Copilot Chat
(**Test Author** mode):

```
Add regression tests (not integration — unit level is fine) that pin the CURRENT
behaviour we must preserve through the soft-delete change:
- creating a task still works and returns 201
- updating a task still works
- posting a comment to a LIVE task still works
- status filtering still returns the right tasks
Put them in the existing test files. They should pass right now, unchanged.
```

Run them — they pass. Commit: `git commit -am "T01: regression tests pinning pre-change behaviour"`.

## Step 3 — Implement, minimal-change, task by task

```
/speckit.implement
```

As it works, hold it to the **minimal-change strategy** (deck, slide 10):

| Do | Don't |
|----|-------|
| Change only what the feature requires | Refactor nearby code "while you're in there" |
| Stay within the blast radius from `change-impact.md` | Touch Ring 3 files |
| Follow the existing pattern (the default filter goes in the **repository**, one place) | Add the `deleted_at IS NULL` check in three different query methods |
| Update `usecase.md` for the changed DELETE contract | Leave the contract doc stale |

Verify after each task. Key checkpoints:

- **Schema:** `deleted_at` column added to `database/schema.sql`; loads clean.
- **Repository:** every read method excludes `deleted_at IS NOT NULL` by default,
  via **one** shared filter — not copy-pasted.
- **Endpoints:** `DELETE` soft-deletes (still `204`); `POST .../restore` works;
  `?permanent=true` hard-deletes; `?deleted=true` lists deleted.
- **Cascade:** comments survive a soft delete and return on restore.
- **Stats:** `GET /api/tasks/stats` (Module 03) still excludes deleted — check
  its query got the shared filter too.

Commit per task, recording the hash in `traceability.md`.

## Step 4 — Run the full suite AFTER, and diff

**macOS / Linux**

```bash
{ cd backend-python && pytest -q ; cd ../frontend && npm test -- --run ; cd .. ; } 2>&1 | tee /tmp/suite-after.txt
diff /tmp/suite-before.txt /tmp/suite-after.txt || true
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q *>&1 | Tee-Object $env:TEMP\suite-after.txt ; cd ..
cd frontend ; npm test -- --run *>&1 | Tee-Object -Append $env:TEMP\suite-after.txt ; cd ..
Compare-Object (Get-Content $env:TEMP\suite-before.txt) (Get-Content $env:TEMP\suite-after.txt)
```

Complete `regression-report.md`:

- Every test that changed must be in the **"intentionally changed"** table with
  a spec reference (e.g. "the DELETE test now asserts `deleted_at` is set and
  the row is hidden, per REQ-0x").
- Any test that broke and is **not** in that table is a real regression — fix
  the code, not the test.
- New regression tests from Step 2 + any added for the new behaviour are listed.

## Step 5 — Port + parity + release readiness

- Use the `port-endpoint` skill (Module 02) to apply soft-delete to a second
  backend; run `compare-responses.sh` for the delete/restore/list-deleted paths.
- Copy `release-readiness-template.md` to
  `specs/002-task-soft-delete/release-readiness.md`, fill it — including the
  **Change safety** section (before/after suite, changed-test justification,
  stayed-in-blast-radius).
- Open the PR; Copilot code review; human approval.

## Step 6 — Greenfield vs Brownfield comparison

**macOS / Linux**

```bash
cp ../module-05/templates/greenfield-vs-brownfield-template.md specs/comparison-greenfield-brownfield.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-05\templates\greenfield-vs-brownfield-template.md specs\comparison-greenfield-brownfield.md
```

Fill it from your **own** experience of Lab 01 vs Labs 02–03. Expected shape of
the answers:

| Dimension | Greenfield (comments) | Brownfield (soft-delete) |
|-----------|----------------------|--------------------------|
| First real step | architecture & conventions | repository archaeology |
| Primary risk | under-specifying the feature | regressing existing behaviour |
| Scope bounded by | the spec | the spec **and** the blast radius |
| Validated against | acceptance criteria | acceptance criteria **+ full regression suite** |
| Time split | mostly writing new tests | mostly reading existing code + changing tests |

Write the one-paragraph takeaway: when is the full archaeology + change-impact
routine worth it, and when is a change small enough to skip it?

## Step 7 — Commit + wrap

```bash
git add specs/ && git commit -m "Module 05 Lab 03: soft-delete implemented, regression report, comparison"
git push
```

## Verify

- [ ] Regression tests were added and committed **before** any behaviour change.
- [ ] The full pre-existing suite passes after the change; every changed test is
      justified in `regression-report.md`.
- [ ] The `deleted_at IS NULL` filter lives in exactly one shared place in the
      repository (and stats reuses it).
- [ ] `compare-responses` shows parity for the new paths across backends.
- [ ] `release-readiness.md` (Change safety section included) verdict is
      "release-ready".
- [ ] `specs/comparison-greenfield-brownfield.md` is filled from real experience,
      with the takeaway paragraph.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Suite has more failures after than the "intentionally changed" list | Real regression. A read path somewhere isn't using the shared filter. Grep for task queries; route them through it. |
| `/speckit.implement` starts refactoring | Interrupt: "minimal change only — do not touch files outside change-impact.md". |
| Stats endpoint now shows wrong counts | Its query didn't get the soft-delete filter — that's a Ring 2 miss from Lab 02. Add it + a test. |
| `restore` brings the task back but comments are gone | Something hard-deleted comments on soft-delete. The cascade must only fire on *permanent* delete. |
| Frontend "six seeded tasks" tests fail | Seed data / fixture expectation changed. Update the test intentionally and log it in the report. |

## Recap — Module 05 complete

The repo now carries, alongside the greenfield feature:

```
specs/
├── 001-task-comments/
│   ├── release-readiness.md          # Lab 01 — greenfield, shipped
│   └── (integration tests, CI gates in .github/workflows/ci.yml)
├── 002-task-soft-delete/
│   ├── archaeology.md                # Lab 02 — what existed
│   ├── change-impact.md              # Lab 02 — the blast radius
│   ├── spec.md / plan.md / tasks.md  # Lab 02 — scoped to the radius
│   ├── regression-report.md          # Lab 03 — before/after, justified
│   └── release-readiness.md          # Lab 03 — change-safety included
└── comparison-greenfield-brownfield.md  # Lab 03 — same discipline, two shapes
```

You have run the full SDLC greenfield **and** brownfield, on the same codebase,
with every change traceable and every pre-existing test protected. **Module 06**
derives a test strategy from this work and proves it catches a deliberately
injected defect.
