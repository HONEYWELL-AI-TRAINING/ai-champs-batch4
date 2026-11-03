# Lab 03 — End-to-End Flow + Defect Injection

**Time:** ~40 min · **Surface:** Copilot Chat + terminal ·
**Prereq:** Lab 02 complete (integration + contract tests green)

## Objective

Add one end-to-end test for the delete → restore flow, then **inject known
defects** into the feature and prove each is caught — by a specific test, at a
specific layer, in seconds. Produce the defect-injection report that reframes a
caught bug as cost avoided.

## Why it matters for the enterprise

A test suite you have never seen fail is a hypothesis. Defect injection turns it
into evidence: "our strategy catches a missing `deleted_at` filter in 3 seconds
at the integration layer" is a statement you can put in front of a sceptical
lead. And every defect caught in CI instead of production is a number Module 11's
ROI model uses directly.

## Step 1 — One end-to-end test

E2E is the top of the pyramid — **few, slow, high-value**. One is enough here.

In Copilot Chat (Agent mode):

```
Add a single end-to-end test for the soft-delete flow. It should exercise the
real stack as far as this project allows:
- start the app against the Testcontainers Postgres
- create a task via POST /api/tasks
- add a comment via POST /api/tasks/{id}/comments
- DELETE the task (soft)
- assert it's absent from GET /api/tasks and GET /api/tasks/stats
- assert GET /api/tasks?deleted=true shows it
- POST /api/tasks/{id}/restore
- assert it's back in GET /api/tasks AND its comment is still there
Put it in tests/test_e2e_soft_delete.py, marked @pytest.mark.integration and
@pytest.mark.e2e. Keep it to ONE test function.
```

If you run a browser E2E tool for the frontend (Playwright/Cypress), add the
board-level version too: delete on the card → gone → "Deleted tasks" view →
restore → back. Otherwise the API-level flow above is the E2E for this module.

Run the full suite and record the baseline:

**macOS / Linux**

```bash
cd backend-python && pytest -q ; cd ../frontend && npm test -- --run ; cd ..
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q ; cd ..\frontend ; npm test -- --run ; cd ..
```

## Step 2 — Set up the injection report

**macOS / Linux**

```bash
git checkout -b m06-defect-injection
cp ../module-06/templates/defect-injection-template.md specs/002-task-soft-delete/defect-injection-report.md
```

**Windows (PowerShell)**

```powershell
git checkout -b m06-defect-injection
Copy-Item ..\module-06\templates\defect-injection-template.md specs\002-task-soft-delete\defect-injection-report.md
```

Record the baseline test counts at the top.

## Step 3 — Inject defects, one at a time

For **each** defect: make the change by hand, run the suite, record which test
failed (name + layer) and how long the run took, then `git checkout -- .` to
revert before the next.

### Defect 1 — a read path forgets the filter

In the repository, remove `WHERE deleted_at IS NULL` (or the shared filter call)
from **one** list/get method — e.g. `get_task_by_id`.
Expected catch: an integration test asserting a soft-deleted task returns `404`.

### Defect 2 — restore doesn't clear the marker

In the restore path, comment out the line that sets `deleted_at = NULL` (make it
a no-op that still returns `200`).
Expected catch: the integration test asserting the task reappears after restore,
and/or the E2E test.

### Defect 3 — permanent delete stops cascading

Change `?permanent=true` to soft-delete instead of hard-delete (or drop the
cascade).
Expected catch: the integration test asserting `task_comments` rows are gone
after a permanent delete.

### Defect 4 (stretch) — a subtle contract break

Make `GET /api/tasks?deleted=true` return the wrong key casing or omit a field.
Expected catch: a **contract** test.

## Step 4 — Handle any misses

If a defect is **not** caught, that's the real finding:

- Which acceptance criterion had no real test, or had it at the wrong layer?
- Add the missing test (on `m06-defect-injection` is fine — you'll cherry-pick
  it back).
- Re-inject; confirm it's now caught.
- Fill the "Defects NOT caught" table.

## Step 5 — Cost-avoided framing

Fill the cost-avoided table. For each defect: where would it have surfaced if the
test didn't exist (a broken board in staging? a customer seeing deleted tasks?
data loss on "restore"?) and roughly what that costs to diagnose, fix, and
hotfix. Defect 2 ("restore silently does nothing") and Defect 3 ("permanent
delete loses comments") are the expensive ones — name why.

## Step 6 — Keep the good tests, drop the branch

Cherry-pick any **new tests** you added in Step 4 back to `module-06-testing`;
discard every injected defect.

```bash
git checkout module-06-testing
git checkout m06-defect-injection -- backend-python/tests/   # bring back only test files
git add -A && git commit -m "Module 06 Lab 03: E2E test + defect-injection report + gap-closing tests"
git branch -D m06-defect-injection
git push
```

Move `defect-injection-report.md` onto `module-06-testing` and commit it too if
it isn't already.

## Verify

- [ ] One E2E test covers create → comment → soft-delete → verify hidden →
      restore → verify back with comment.
- [ ] `defect-injection-report.md` has ≥ 3 injected defects, each with the
      catching test named, its pyramid layer, and time-to-detection.
- [ ] Any defect that slipped through has a new test and is now caught.
- [ ] The cost-avoided table is filled with a plausible escape point per defect.
- [ ] The `module-06-testing` branch has the new tests but **none** of the
      injected defects.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| An injected defect breaks 20 tests | Good — but note the *most specific* one (closest layer, clearest name); that's the one doing the work. |
| A defect is caught only by E2E | Push it down: add an integration test for it. E2E catching everything is slow and vague. |
| Nothing catches Defect 1 | A read path genuinely has no test — that's the Module 05 Ring-2 risk realised. Add it. |
| Cherry-pick brings back source changes too | `git checkout <branch> -- backend-python/tests/` restores only the tests dir; verify with `git diff --stat`. |

## Recap — Module 06 complete

Both features now carry:

```
specs/002-task-soft-delete/
├── test-strategy.md              # Lab 01 — criterion → test type, test data, gaps, AC→test map
├── (integration + contract + e2e tests under backend-python/tests/)   # Lab 02–03
└── defect-injection-report.md    # Lab 03 — proven against real defects, cost framed
```

…a spec-derived test pyramid, real dependencies via Testcontainers, and evidence
it catches what matters. **Module 07** governs the agents that do this work —
connecting them to approved tools via MCP and packaging the patterns as
versioned, owned skills.
