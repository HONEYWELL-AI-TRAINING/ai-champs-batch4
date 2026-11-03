# Lab 01 — Greenfield: Carry the Spec to Release-Ready

**Time:** ~60 min · **Surface:** Copilot Chat + terminal + GitHub Actions ·
**Prereq:** Module 05 [set-up](README.md#set-up--do-this-once-before-lab-01) done

## Objective

Take the Module 04 **task comments** feature — implemented and unit-tested, but
not shipped — through the rest of the greenfield SDLC: an architecture &
conventions check, integration tests against a real database, an extended CI
pipeline with **quality gates**, and a **release-readiness** report traced back
to the spec.

## Why it matters for the enterprise

"Copilot wrote the feature" is not "the feature is ready to ship". Release
readiness is a *checklist against the specification* — integration-tested,
gated in CI, reviewed, reversible. Doing this stage deliberately is what turns
AI-assisted coding into AI-assisted **delivery**, and it is the baseline
Module 06's test strategy builds on.

## Background — the greenfield SDLC, and where Copilot helps

```
Specification → Architecture & Conventions → Implementation → Test Strategy → CI / Quality Gates → PR / Release
   (Module 04)         (Step 1)               (M04, verify)     (Step 2)          (Step 3)          (Step 4)
```

Copilot assists at **every** stage, not just implementation: drafting the
integration-test plan from acceptance criteria, writing pipeline YAML, explaining
a gate failure, and summarising the diff for the PR.

---

## Step 1 — Architecture & conventions review

Open a Copilot Chat, switch to the **API Reviewer** chat mode (Module 02, Lab 03),
and attach `specs/001-task-comments/spec.md`, `plan.md`, and the implemented
files. Ask:

```
Review the implemented task-comments feature against plan.md and the
constitution. Confirm: repository-only DB access, error contract (404/422),
schema change is in database/schema.sql only, and the code follows the
conventions of the surrounding files. List anything that drifted during
implementation.
```

Fix any drift now, before adding more tests on top. Commit.

## Step 2 — Integration tests against a real database

Unit tests (Module 04) used fixtures/fakes. Integration tests exercise the real
SQL, the real FK cascade, and the real error paths.

### 2a — Start a test database

**macOS / Linux**

```bash
docker run -d --name tb-itest -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=taskboard_it -p 5433:5432 postgres:16
until docker exec tb-itest pg_isready -U postgres ; do sleep 1 ; done
docker exec -i tb-itest psql -U postgres -d taskboard_it < database/schema.sql
docker exec -i tb-itest psql -U postgres -d taskboard_it < database/seed.sql
```

**Windows (PowerShell)**

```powershell
docker run -d --name tb-itest -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=taskboard_it -p 5433:5432 postgres:16
do { Start-Sleep 1 } until (docker exec tb-itest pg_isready -U postgres)
Get-Content database/schema.sql | docker exec -i tb-itest psql -U postgres -d taskboard_it
Get-Content database/seed.sql   | docker exec -i tb-itest psql -U postgres -d taskboard_it
```

### 2b — Generate the integration tests from acceptance criteria

In Copilot Chat (Agent mode), attach `specs/001-task-comments/acceptance-checklist.md`
and the existing test files:

```
Write integration tests for the task-comments feature that run against a real
Postgres database (DATABASE_URL pointing at localhost:5433/taskboard_it), in a
new file backend-python/tests/test_comments_integration.py.

Cover, from the acceptance checklist:
- GET returns comments oldest-first (real ORDER BY)
- POST persists and the row is really there
- DELETE removes the real row
- deleting a TASK cascades to its comments (real FK ON DELETE CASCADE)
- the 5-minute delete window (if that change from Module 04 Lab 04 is present)

Mark them with a pytest marker `@pytest.mark.integration` so unit runs can skip
them. Reset state between tests (truncate or transaction rollback). Match the
existing test style.
```

Run them:

**macOS / Linux**

```bash
cd backend-python
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5433/taskboard_it" pytest -q -m integration
cd ..
```

**Windows (PowerShell)**

```powershell
cd backend-python
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/taskboard_it"
pytest -q -m integration
cd ..
```

Add a matching frontend integration/E2E check if you run one (e.g. a Vitest test
that mounts the board and drives the comment flow against a mocked API).

## Step 3 — Extend CI with quality gates

You have `.github/workflows/ci.yml` from Module 02, Lab 08. Ask Copilot to
extend it:

```
Extend .github/workflows/ci.yml:
- Add a job "backend-integration" that spins up postgres:16 as a service, loads
  database/schema.sql + seed.sql, and runs `pytest -m integration` for
  backend-python.
- Add a coverage gate to the existing backend job: fail if coverage on changed
  files is below 80% (pytest-cov + diff-cover, or coverage's --fail-under).
- Add a lint job (ruff for Python, the existing oxlint config for the frontend).
- Add a "schema-check" job if it isn't there: load schema.sql then seed.sql into
  a fresh DB, fail on any error.
- Keep official actions/* pinned to major versions; cache pip and npm.
Show me the full file.
```

Review the YAML against the `ci.yml` you already have — reconcile, don't blindly
replace. Push and watch:

```bash
git add -A && git commit -m "Module 05 Lab 01: comments integration tests + CI quality gates"
git push
gh run watch
```

If a gate fails, feed it to Copilot:

```bash
gh run view --log-failed | gh copilot explain -
```

## Step 4 — Release-readiness report + PR

**macOS / Linux**

```bash
cp ../module-05/templates/release-readiness-template.md specs/001-task-comments/release-readiness.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-05\templates\release-readiness-template.md specs\001-task-comments\release-readiness.md
```

Fill every row with evidence. For the PR description, let Copilot draft it from
the spec:

```
Draft a PR description for the task-comments feature. Summarise what changed by
layer, list the acceptance criteria and the test that covers each, note the
schema change, and link the release-readiness report. Base it on
specs/001-task-comments/.
```

Open the PR, let **Copilot code review** run (Module 02, Lab 07), resolve
comments, and get a human approval. Mark the release-readiness verdict.

### Clean up the test container

```bash
docker rm -f tb-itest
```

## Verify

- [ ] The architecture review found and fixed any implementation drift.
- [ ] `pytest -m integration` passes against a real Postgres.
- [ ] `ci.yml` has integration, coverage-gate, lint, and schema-check jobs, and
      the run is green.
- [ ] `specs/001-task-comments/release-readiness.md` is fully evidenced with a
      "release-ready" verdict.
- [ ] The PR has a spec-based description, a passed Copilot review, and a human
      approval.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Integration tests can't connect | Port clash — the lab uses `5433` for the test DB so it doesn't fight your dev DB on `5432`. Match the `DATABASE_URL`. |
| `pytest -m integration` also runs unit tests | Add `markers = integration: real-DB tests` to `pytest.ini` and register the marker; use `-m "integration"` / `-m "not integration"`. |
| Coverage gate fails on unrelated files | Gate on **changed** files only (`diff-cover` against the base branch), not whole-project coverage. |
| CI service container never becomes healthy | Add the `--health-cmd`/`--health-interval` options to the `postgres` service; wait on it before the schema load. |
| FK cascade test fails | The `task_comments` FK needs `ON DELETE CASCADE` in `schema.sql` (Module 04 Lab 02 plan) — verify it's actually there. |

## Recap & carry-forward

The greenfield feature is release-ready, gated, and traceable end to end. **Lab
02** switches tracks: a change to *existing* behaviour, where the first move is
not architecture but **archaeology** — understanding what's already there before
touching it.
