# Lab 04 — Brownfield Soft-Delete with OpenSpec

**Time:** ~60 min · **Surface:** Copilot Chat + terminal ·
**Prereq:** Lab 01 complete; Labs 02–03 read (you may have done them) ·
Node.js 20.19+

> **Same feature, second tool.** Labs 02–03 deliver
> [soft-delete for tasks](feature-request.md) with **Spec Kit**. This lab
> delivers the **same request** with **OpenSpec**, so you can compare the two on
> a brownfield change. Pick one route:
>
> - **Instead of Labs 02–03** — branch from your Lab 01 result and do this lab.
> - **After Labs 02–03** — branch from the commit *just before* the Lab 03
>   soft-delete implementation (the comparison is fairer when both start from
>   the same code). Don't build it twice on one branch.

## Objective

Make `DELETE /api/tasks/{id}` recoverable using OpenSpec's
**propose → apply → archive** loop:

1. Understand the blast radius first (archaeology + change impact — Lab 02's method).
2. Capture today's behaviour as a **baseline spec**.
3. Propose the change as **delta specs** (`MODIFIED` + `ADDED` requirements).
4. Implement from `tasks.md` — regression tests first — and prove the
   pre-existing suite still passes.
5. Archive, so the living spec describes the system *after* the change.

## Why it matters for the enterprise

On brownfield code the risk is the regression, not the new endpoint. A
soft-delete request reads like one feature but rewrites the meaning of
"the task is gone" in every read path, the comment cascade, the stats endpoint,
and a frontend test that expects six seeded tasks. OpenSpec fits this shape of
work: each change is a **self-contained folder of deltas** against a spec of
what the system does today — small enough to review in a PR before code, and
merged into the living spec when done.

Spec Kit builds the whole artifact chain for a feature; OpenSpec records only
what *changes* relative to the current spec. Neither replaces archaeology and
impact analysis — they are what make the delta **complete**.

## Background — OpenSpec in 60 seconds

```
openspec/
├── specs/                      # source of truth: what the system DOES today
│   └── <capability>/spec.md
└── changes/                    # proposals in flight
    ├── <change-name>/
    │   ├── proposal.md         # why + scope + approach
    │   ├── design.md           # technical decisions
    │   ├── tasks.md            # numbered checklist the agent works through
    │   └── specs/<capability>/spec.md   # DELTAS: ADDED / MODIFIED / REMOVED
    └── archive/YYYY-MM-DD-<change-name>/   # finished changes
```

| Step | Copilot Chat (VS Code) | What happens |
|------|------------------------|--------------|
| Think (optional) | `/opsx-explore` | Investigate code and options; writes nothing unless you ask |
| Propose | `/opsx-propose <name>` | Creates `proposal.md`, delta specs, `design.md`, `tasks.md` |
| Revise | `/opsx-update` | Edits those artifacts (never code) and keeps them consistent |
| Apply | `/opsx-apply` | Implements `tasks.md`, ticking boxes |
| Archive | `/opsx-archive` | Merges deltas into `openspec/specs/`, moves the change to `archive/` |

In Copilot Chat the commands are hyphenated (`/opsx-propose`); OpenSpec docs
write `/opsx:propose`. Same thing.

**Delta format** — the heart of the tool:

```markdown
## ADDED Requirements
### Requirement: Restore a deleted task
The system SHALL ...
#### Scenario: Restore succeeds
- **WHEN** ...
- **THEN** ...

## MODIFIED Requirements
### Requirement: Delete a task
<the FULL updated requirement text, replacing the old one>
```

> **OpenSpec moves quickly.** This lab uses the current `/opsx-*` workflow.
> Older installs use `/openspec:proposal`, `/openspec:apply`,
> `/openspec:archive`. Run `openspec --help` and see the
> [OpenSpec docs](https://github.com/Fission-AI/OpenSpec) if something differs —
> the *method* below is stable.

---

## Step 0 — Branch and snapshot the suite BEFORE

Route A (instead of Labs 02–03):

```bash
git checkout module-05-sdlc
git checkout -b module-05-openspec-soft-delete
```

Route B (after Labs 02–03): create the branch from the commit before the
soft-delete implementation (`git log --oneline` to find it):

```bash
git checkout -b module-05-openspec-soft-delete <commit-before-lab-03-implement>
```

Snapshot the baseline, exactly as in Lab 03 — you will diff against it at the end.

**macOS / Linux**

```bash
{ cd backend-python && pytest -q ; cd ../frontend && npm test -- --run ; cd .. ; } 2>&1 | tee /tmp/openspec-before.txt
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q *>&1 | Tee-Object $env:TEMP\openspec-before.txt ; cd ..
cd frontend ; npm test -- --run *>&1 | Tee-Object -Append $env:TEMP\openspec-before.txt ; cd ..
```

Note the counts (e.g. `pytest 19 passed`, `vitest 12 passed`).

## Step 1 — Understand before you touch (archaeology + blast radius)

OpenSpec does not do this for you; a delta spec is only as complete as your
understanding of the code. If you already completed Lab 02, **reuse your
`archaeology.md` and `change-impact.md`** and skip to Step 2.

Otherwise, produce short versions. Keep them next to the change, outside
`openspec/`:

**macOS / Linux**

```bash
mkdir -p docs/soft-delete-openspec
cp ../module-05/templates/archaeology-template.md   docs/soft-delete-openspec/archaeology.md
cp ../module-05/templates/change-impact-template.md docs/soft-delete-openspec/change-impact.md
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force -Path docs\soft-delete-openspec | Out-Null
Copy-Item ..\module-05\templates\archaeology-template.md   docs\soft-delete-openspec\archaeology.md
Copy-Item ..\module-05\templates\change-impact-template.md docs\soft-delete-openspec\change-impact.md
```

In Copilot Chat (Ask mode), one question at a time, verifying each path you are
given by opening the file:

```
#codebase I'm changing DELETE /api/tasks/{id} from hard delete to soft delete.
1. Trace the current delete path end to end, from the React services layer to
   the tasks table.
2. List every repository/query method that reads tasks (list, get, filter,
   count, stats).
3. Show the existing tests that assert a task is GONE after DELETE, and any
   test that assumes six seeded tasks.
4. What depends on DELETE cascading to task_comments today?
Paths and function names only.
```

Fill the **ring** sections of `change-impact.md` (Ring 1 repository + delete path +
comment cascade; Ring 2 `GET /api/tasks/stats`, the frontend board and its
"six seeded tasks" tests, seed data, `usecase.md`; Ring 3 create / update /
comment-on-live-task / status filter, each with the test that guards it).

This list is your **checklist for reviewing the delta spec** in Step 4.

## Step 2 — Install and initialise OpenSpec

```bash
node --version                                  # 20.19 or newer
npm install -g @fission-ai/openspec@latest      # or: brew install openspec
openspec --version
openspec init --tools github-copilot
```

When asked about the GitHub cloud coding agent files, answer **No** for this lab.

**macOS / Linux**

```bash
ls openspec openspec/specs openspec/changes
ls .github/prompts | grep opsx
```

**Windows (PowerShell)**

```powershell
dir openspec ; dir openspec\specs ; dir openspec\changes
dir .github\prompts | findstr opsx
```

You should see `openspec/specs/`, `openspec/changes/`, `openspec/config.yaml`,
and `opsx-*.prompt.md` files in `.github/prompts/` (plus generated skills under
`.github/skills/`). Commit it — tooling, separate from the feature:

```bash
git add -A && git commit -m "chore: initialise OpenSpec"
```

> **Coexists with the Module 02–04 layer.** `.github/copilot-instructions.md`,
> instructions, prompts, agents, skills, and Spec Kit's `.specify/` are
> untouched; OpenSpec adds its own files. If prompt names clash, keep both and
> tell your facilitator.

Add project context so every proposal inherits your conventions. In
`openspec/config.yaml`, edit only the `context` value:

```yaml
context: |
  Task Board: React (Vite) frontend; .NET, Python (FastAPI) and Java backends over PostgreSQL.
  Layering: Controller/Router -> Service -> Repository; all SQL in repositories.
  React: components -> pages -> services; all HTTP in services/.
  Error contract: 404 missing, 422 bad request. No other codes without a constitution-level decision.
  Brownfield: minimal change; stay inside the blast radius; do not edit applied migrations.
  All backends must be behaviour-identical (status codes, bodies, ordering).
```

## Step 3 — Baseline spec of today's behaviour

A `MODIFIED` requirement needs an existing requirement to modify, so describe
what the code does **now**, including the Ring 2 behaviour (stats, comments):

```
/opsx-explore

Read the task endpoints, the stats endpoint, and the comment endpoints in
backend-python (router, service, repository) plus their tests. Do not change
code. Write openspec/specs/task-management/spec.md describing the CURRENT
behaviour of: list tasks (status filter), get one, create, update, delete,
GET /api/tasks/stats, and posting/listing comments on a task. Use
"### Requirement:" headings with SHALL statements and "#### Scenario:" blocks
with WHEN/THEN bullets. Include exact status codes (success, 404, 422) and say
what happens to comments when a task is deleted today. Describe only what the
code does.
```

> If `/opsx-explore` will not write files, reply *"Yes, write the file now."*,
> or use plain Copilot Chat in Agent mode.

Review it as you would code:

- [ ] `Delete a task` states the real success status (`204`) and the `404` case.
- [ ] It says the row is **physically removed** and comments cascade — the
      behaviour you are about to change.
- [ ] Stats and comments requirements exist (they are in your blast radius).
- [ ] Nothing invented. If you cannot find it in code or a test, delete it.

```bash
openspec validate --specs
git add -A && git commit -m "docs: baseline task-management spec"
```

## Step 4 — Propose the change

Open a **fresh Copilot Chat**. Give it the request and your decisions — the
same ones Lab 02 suggests, so the comparison with Spec Kit is like for like:

```
/opsx-propose soft-delete-tasks

Implement labs/module-05/feature-request.md.

Decisions:
- Marker: deleted_at TIMESTAMP NULL (null = active), added by a NEW numbered
  migration; add the column to database/schema.sql as well. Never edit an
  applied migration.
- DELETE /api/tasks/{id} soft-deletes and keeps returning 204.
- GET /api/tasks/{id} on a deleted task is 404 by default; 200 only with
  ?includeDeleted=true.
- List deleted: GET /api/tasks?deleted=true.
- Restore: POST /api/tasks/{id}/restore. Permanent delete:
  DELETE /api/tasks/{id}?permanent=true.
- Deleted tasks are excluded from /api/tasks/stats.
- POST/GET comments on a deleted task: 404. Comments survive a soft delete and
  are visible again after restore; the comment cascade fires ONLY on permanent
  delete.
- Error contract unchanged: 404 / 422 only.
- The "exclude deleted" filter lives in ONE shared place in the repository.
- Out of scope: auto-purge, retention, bulk operations, auditing who deleted.

Context: docs/soft-delete-openspec/change-impact.md lists the blast radius. Stay
inside it. Record decisions and the existing tests that must be UPDATED in
design.md.
```

It creates `openspec/changes/soft-delete-tasks/`. **Do not run `/opsx-apply` yet.**

```bash
openspec list
openspec show soft-delete-tasks
openspec validate soft-delete-tasks --strict
```

### Review checklist — the main skill in this lab

**Delta spec (`specs/task-management/spec.md`)**

- [ ] `MODIFIED`: **Delete a task** (full new text: row kept and marked, still `204`).
- [ ] `MODIFIED`: every requirement whose behaviour changes — **list**, **get
      one**, **update**, **stats**, **post comment**, **list comments**.
      Compare against your Ring 1 + Ring 2 list. A missing one is a regression
      you chose to ship.
- [ ] `ADDED`: **Restore**, **List deleted**, **Permanent delete**, each with
      happy-path *and* edge scenarios (restore of a live task, permanent delete
      of an already-soft-deleted task, unknown id).
- [ ] Comments: scenario that comments survive soft delete and reappear on restore.
- [ ] Each scenario is testable from its WHEN/THEN alone; no new status codes.

**`design.md`**
- [ ] One shared "active tasks" filter in the repository; stats and comments reuse it.
- [ ] Lists the existing tests that must change (the "row is gone" assertion,
      the six-task frontend expectation) and why that is correct.
- [ ] Open questions from `feature-request.md` each answered with a reason.

**`tasks.md`**
- [ ] **First group is regression tests** pinning create / update / comment-on-live /
      status-filter — *before* any behaviour change.
- [ ] Then: migration → repository → service → router → tests → frontend → docs.
- [ ] Tests live inside each group, not in a final catch-up group.

### Fix the spec, not the code

```
/opsx-update soft-delete-tasks

The delta does not modify the stats requirement. Add a MODIFIED requirement so
/api/tasks/stats excludes soft-deleted tasks, with a scenario. Keep design.md
and tasks.md consistent. Do not touch code.
```

Iterate until `openspec validate soft-delete-tasks --strict` passes, then commit the
proposal **alone** — the commit a teammate would approve before any code exists:

```bash
git add -A && git commit -m "spec: propose soft-delete-tasks"
```

## Step 5 — Apply: regression tests first, then the Python backend

```
/opsx-apply soft-delete-tasks

Do the first task group only: add the regression tests that pin CURRENT
behaviour. They must pass unchanged on the current code. Stop there.
```

```bash
cd backend-python && pytest -q ; cd ..          # still green, now with new tests
git add -A && git commit -m "T01: regression tests pinning pre-change behaviour"
```

Now the change itself, still minimal-change:

```
/opsx-apply soft-delete-tasks

Continue through the migration and Python backend task groups. Follow the
minimal-change rules: touch only files in docs/soft-delete-openspec/change-impact.md,
follow existing patterns, no refactoring. Write each new test from the
WHEN/THEN of its scenario before the code that satisfies it. Stop before the
frontend.
```

Review the diff against the spec:

- [ ] New numbered file in `database/migrations/`; no applied migration edited.
- [ ] `deleted_at IS NULL` appears in **one** shared place; stats and comment
      lookups reuse it. (`grep -rn "deleted_at" backend-python` — a handful of
      hits, not one per query.)
- [ ] `DELETE` still `204`; `?permanent=true` is the only path that removes rows
      or cascades to comments.
- [ ] Each scenario has a test whose name makes the link obvious.

Smoke test (use the spec's routes if they differ):

```bash
curl -i -X DELETE http://localhost:8000/api/tasks/1             # 204
curl -i http://localhost:8000/api/tasks/1                       # 404
curl -s "http://localhost:8000/api/tasks?deleted=true"          # lists task 1
curl -s http://localhost:8000/api/tasks/stats                   # excludes it
curl -i -X POST http://localhost:8000/api/tasks/1/restore       # back, comments intact
curl -i -X DELETE "http://localhost:8000/api/tasks/1?permanent=true"
```

```bash
git add -A && git commit -m "feat(python): soft delete tasks"
```

## Step 6 — Apply: port a second backend and the board

```
/opsx-apply soft-delete-tasks

Continue with a second backend (.NET), then the frontend task groups. Mirror
the behaviour from the delta spec — the spec is the contract, not the Python
code. Update the six-seeded-tasks expectation and usecase.md as design.md says.
```

(Or use the `port-endpoint` skill from Module 02 for the port.) Then:

**macOS / Linux**

```bash
(cd backend-dotnet && dotnet test)
(cd frontend && npm test -- --run && npm run build)
```

**Windows (PowerShell)**

```powershell
cd backend-dotnet ; dotnet test ; cd ..
cd frontend ; npm test -- --run ; npm run build ; cd ..
```

Run `compare-responses.sh` for delete, restore, list-deleted, and permanent
paths. In the browser: deleting a card drops the column count; a **Deleted**
view lists it with **Restore**; search and filter never show it; and the empty
Deleted view looks different from an empty board.

```bash
git add -A && git commit -m "feat: soft delete on second backend and board"
```

## Step 7 — Regression report, verify, archive

Re-run the full suite and diff against Step 0:

**macOS / Linux**

```bash
{ cd backend-python && pytest -q ; cd ../frontend && npm test -- --run ; cd .. ; } 2>&1 | tee /tmp/openspec-after.txt
diff /tmp/openspec-before.txt /tmp/openspec-after.txt || true
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q *>&1 | Tee-Object $env:TEMP\openspec-after.txt ; cd ..
cd frontend ; npm test -- --run *>&1 | Tee-Object -Append $env:TEMP\openspec-after.txt ; cd ..
Compare-Object (Get-Content $env:TEMP\openspec-before.txt) (Get-Content $env:TEMP\openspec-after.txt)
```

Write `docs/soft-delete-openspec/regression-report.md` using the same shape as Lab 03
(baseline counts, **intentionally changed tests** with the delta-spec scenario
that justifies each, after counts). A test that broke and is *not* justified by
a scenario is a real regression — fix the code, not the test.

Then check coverage of the spec:

```
Walk every Scenario in openspec/changes/soft-delete-tasks/specs/ and name the
test (backend, file, test name) that proves each. List any scenario with no
test. Do not edit files.
```

Close the gaps, then archive:

```
/opsx-archive soft-delete-tasks
```

(or `openspec archive soft-delete-tasks --yes`).

```bash
ls openspec/changes/archive
openspec validate --specs
git add -A && git commit -m "spec: archive soft-delete-tasks"
git push -u origin module-05-openspec-soft-delete
```

`openspec/specs/task-management/spec.md` now describes the system **after** the
change; the archived folder keeps the proposal, design, and deltas as the
permanent "why". Open the PR, link the archived change, and run Copilot code
review.

## Step 8 — Compare with Spec Kit

Fill in from real experience (use your Labs 02–03 notes if you did them, or the
`greenfield-vs-brownfield` template's questions if not):

| Question | Spec Kit (Labs 02–03) | OpenSpec (this lab) |
|----------|----------------------|---------------------|
| What did you write first? | | |
| Where is the "why" of this change afterwards? | | |
| What did each tool do to find the blast radius? | | (Step 1 was manual) |
| How many artifacts did the one change produce? | | |
| What describes system behaviour *today*? | | |
| Which was lighter for this brownfield change? | | |
| Which would you use for a brand-new feature? | | |

One-paragraph takeaway: what did the spec tool contribute, and what still had
to come from archaeology, impact analysis, and regression tests?

## Stretch — a change to the change

*"Deleted tasks older than 30 days should be hidden from the Deleted view."*
Run `/opsx-propose deleted-view-30-day-window` without opening any code.

- Which one requirement does it `MODIFY`?
- Did it notice that "auto-purge" stays out of scope?
- How small is the new `tasks.md`?

## Verify

- [ ] Regression tests were committed **before** any behaviour change.
- [ ] The proposal commit exists **before** any implementation commit.
- [ ] The delta `MODIFIED` list covers every Ring 1 and Ring 2 item (delete,
      list, get, update, stats, comments).
- [ ] The migration is a new file; `deleted_at IS NULL` lives in one shared place.
- [ ] Full pre-existing suite passes; every changed test is justified by a scenario.
- [ ] Every delta scenario maps to a named test; parity shown with `compare-responses`.
- [ ] `openspec validate --specs` passes after archiving; the living spec
      reflects soft delete.
- [ ] Comparison table and takeaway are filled from real experience.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `/opsx-propose` missing in Copilot Chat | Prompt files work in IDE extensions only (not Copilot CLI). Check `ls .github/prompts`, run `openspec update`, reload VS Code. |
| Commands are `/openspec:proposal` etc. | Older OpenSpec. `npm install -g @fission-ai/openspec@latest && openspec update`, or use the legacy names — same steps. |
| Delta only changes `DELETE` | Hand the agent your `change-impact.md` Ring 2 list and `/opsx-update` the missing `MODIFIED` requirements. |
| `validate`: requirement has no scenario | Each `### Requirement:` needs a `#### Scenario:` (exactly four `#`). |
| `validate`: MODIFIED requirement not found | The heading must match the baseline spec's requirement name exactly. |
| Agent starts refactoring | Interrupt: "minimal change only — do not touch files outside change-impact.md." |
| `restore` works but comments are gone | Something deletes comments on soft delete. The cascade must fire only on permanent delete. |
| Stats counts are wrong | The stats query missed the shared filter — a Ring 2 miss. Add it, plus a test. |
| Frontend "six seeded tasks" tests fail | Update the expectation intentionally and log it in the regression report. |
| `openspec archive` hangs in a script | Add `--yes`. |

## Recap — Module 05 complete (OpenSpec track)

```
openspec/
├── config.yaml
├── specs/task-management/spec.md              # living spec — now includes soft delete
└── changes/archive/<date>-soft-delete-tasks/  # proposal, design, tasks, deltas
docs/soft-delete-openspec/
├── archaeology.md · change-impact.md          # what existed, what it touches
└── regression-report.md                       # before/after, justified
```

You delivered the same brownfield change two ways and can say what each tool
gives you — and what neither replaces: understanding the code before changing
it, and proving the old behaviour still holds. **Module 06** derives a test
strategy from this work and proves it catches a deliberately injected defect.
