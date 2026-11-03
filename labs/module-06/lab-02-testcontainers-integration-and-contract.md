# Lab 02 — Testcontainers Integration & Contract Tests

**Time:** ~45 min · **Surface:** Copilot Chat (Agent) + terminal + CI ·
**Prereq:** Lab 01 complete (`test-strategy.md` exists); Docker running

## Objective

Build the integration layer of the pyramid with **Testcontainers** — the
strategy's "needs a real database" rows run against an ephemeral Postgres that
spins up fresh per run. Add **API/contract** tests that pin the HTTP contract in
`usecase.md`. Wire both into CI.

## Why it matters for the enterprise

A mock of a database is a guess about how the database behaves. `WHERE deleted_at
IS NULL`, `ON DELETE CASCADE`, unique constraints, transaction rollback — these
only tell the truth against a real engine. Testcontainers gives you that truth
without paying full end-to-end cost for every scenario, and the **same**
behaviour in CI as on your laptop.

## Background — Testcontainers vs mocks

| Testcontainers | Mocks & stubs |
|----------------|---------------|
| Real Postgres in an ephemeral container | DB behaviour guessed at |
| Same result in CI as in prod | Passes in CI, fails against the real service |
| Version pinned to match prod (`postgres:16`) | Config drift accumulates silently |
| Trustworthy integration coverage | False confidence |

Per language: Python `testcontainers[postgres]` · .NET `Testcontainers.PostgreSql`
· Java `org.testcontainers:postgresql` · Node `@testcontainers/postgresql`.
Steps below show **Python**; the pattern is identical elsewhere.

---

## Step 1 — Add the dependency

**macOS / Linux**

```bash
cd backend-python
printf '\ntestcontainers[postgres]>=4.8\npytest-cov>=5\n' >> requirements-dev.txt 2>/dev/null || printf 'testcontainers[postgres]>=4.8\npytest-cov>=5\n' > requirements-dev.txt
pip install -r requirements-dev.txt
cd ..
```

**Windows (PowerShell)**

```powershell
cd backend-python
Add-Content requirements-dev.txt "testcontainers[postgres]>=4.8`npytest-cov>=5"
pip install -r requirements-dev.txt
cd ..
```

(If the backend keeps all deps in `requirements.txt`, add them there instead —
match the project's convention.)

## Step 2 — A session-scoped Postgres fixture

In Copilot Chat (Agent mode), attach `backend-python/tests/conftest.py`,
`database/schema.sql`, and `specs/002-task-soft-delete/test-strategy.md`:

```
Add a pytest fixture in tests/conftest.py that:
- starts a postgres:16 container via testcontainers (session scope),
- loads database/schema.sql and database/seed.sql into it,
- exposes its connection URL as an env var / settings override so the FastAPI
  app and repositories talk to the container,
- truncates the tables (or wraps each test in a rolled-back transaction) between
  tests so they're isolated,
- is marked so `-m "not integration"` skips anything that needs it.

Match the existing fixture style. Show me conftest.py before writing.
```

Register the marker in `pytest.ini`:

```ini
[pytest]
markers =
    integration: tests that need a real database (Testcontainers)
```

## Step 3 — Write the integration tests from the strategy

```
Using specs/002-task-soft-delete/test-strategy.md, implement every row marked
"integration" as a test in tests/test_soft_delete_integration.py, using the
Testcontainers fixture. Cover at least:
- a read path returns only non-deleted tasks (real WHERE)
- restore clears deleted_at and the task reappears
- ?permanent=true hard-deletes AND cascades to task_comments
- soft delete does NOT remove task_comments
- GET /api/tasks/stats (Module 03) excludes soft-deleted tasks
- the "deleted_at filter missing" failure case is caught (write the test so it
  would fail if any read method forgot the filter)
Mark them @pytest.mark.integration. Match the existing test style.
```

Run them:

**macOS / Linux**

```bash
cd backend-python && pytest -q -m integration ; cd ..
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q -m integration ; cd ..
```

## Step 4 — Contract tests

Attach `usecase.md` (the API-contract section) and ask:

```
Add contract tests in tests/test_contract.py that assert the HTTP contract from
usecase.md for the task endpoints, INCLUDING the soft-delete additions:
- method + path + success status for each route
- the response body shape (field names, types, nullability) for GET list, GET
  one, POST, PUT, DELETE, restore, and GET ?deleted=true
- the error contract: 404 shape, 422 shape, and (from Module 04 Lab 04) 409 if
  the delete-window rule is present
These run against the app + Testcontainers DB. If usecase.md and the code
disagree, tell me which is wrong — don't just make the test pass.
```

## Step 5 — Wire into CI

Extend `.github/workflows/ci.yml` (or the integration job from Module 05 Lab 01):

```
Update .github/workflows/ci.yml so the backend-integration job runs
`pytest -m integration` and `pytest tests/test_contract.py`. Testcontainers
needs Docker — GitHub-hosted ubuntu runners have it; make sure the job doesn't
also start a separate `services: postgres` (Testcontainers manages its own).
Add a coverage report (pytest-cov) and fail if changed-file coverage < 80%.
```

Push and watch:

```bash
git add -A && git commit -m "Module 06 Lab 02: Testcontainers integration + contract tests"
git push && gh run watch
```

## Step 6 — Record the comparison

Add a short section to `test-strategy.md`:

- Which tests moved from mock/fixture to Testcontainers, and what each now
  proves that it couldn't before.
- Runtime cost: unit suite vs integration suite (seconds). This is why the
  pyramid has few of the slow ones.

## Verify

- [ ] `pytest -m "not integration"` still runs fast and green (unit layer intact).
- [ ] `pytest -m integration` spins up a container, loads the schema, and passes.
- [ ] Tests are isolated — running them in any order gives the same result.
- [ ] Contract tests fail if you rename a response field (try it, then revert).
- [ ] CI runs both and enforces the coverage gate; the run is green.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `docker not found` in tests | Docker Desktop not running. `docker info` must succeed first. |
| Container start is slow every test | Fixture is function-scoped — make it **session**-scoped; isolate with truncate/rollback, not restart. |
| CI: Testcontainers can't reach Docker | Use `ubuntu-latest` (has Docker). Don't run it inside a container-job without docker-in-docker. |
| Tests pass alone, fail together | State leaks between tests — the truncate/rollback step isn't running. |
| Coverage gate fails on untouched files | Gate on **changed** files (`diff-cover` vs the base branch), not whole-project. |

## Recap & carry-forward

The integration and contract layers are real and trustworthy. **Lab 03** adds a
thin end-to-end test and then breaks the feature on purpose to prove the whole
strategy catches it.
