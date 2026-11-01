# Lab 08 — Copilot CLI + Authoring GitHub Actions Workflows

**Time:** ~20 min · **Surface:** Terminal (macOS / Linux / Windows) + GitHub.com ·
**Prereq:** Labs 01 and 06 complete; `gh` installed and authenticated

## Objective

Use Copilot from the **terminal** — both the `gh copilot` command helper and the
agentic `copilot` CLI — against the Task Board repo, then have it author the
**CI workflow** that builds and tests the project (the workflow Lab 06's
setup-steps assumed exists).

## Why it matters for the enterprise

Not all engineering happens in an editor. DevOps and SRE work — pipelines,
scripts, incident triage — is terminal-first. The CLI brings the same governed
Copilot (same account, same policies, same repo instruction files) to that
surface, so shell work gets the same assistance and the same guardrails.

## Background — two CLI tools

| Tool | Install | Use for |
|------|---------|---------|
| **`gh copilot`** (extension) | `gh extension install github/gh-copilot` | One-shot: *explain this command*, *suggest a command for X* |
| **`copilot`** (agentic CLI) | `npm install -g @github/copilot` then `copilot` | Multi-step agent work in a repo: read files, edit, run commands, open PRs — reads `AGENTS.md` / `.github/copilot-instructions.md` |

Both authenticate with your GitHub account (`gh auth login`, or the CLI's own
`/login`). Enterprise policy applies to both.

---

## Part A — `gh copilot` for command help

### Step 1 — Install

**macOS / Linux / Windows (PowerShell)** — same command:

```bash
gh extension install github/gh-copilot
gh copilot --version
```

### Step 2 — Explain

```bash
gh copilot explain "docker exec -i taskboard-db psql -U postgres -d taskboard < database/schema.sql"
```

Read the breakdown — this is the Module 01 schema-load command; the explanation
is useful onboarding material.

### Step 3 — Suggest

```bash
gh copilot suggest "run only the Python task-service tests and show the slowest 3"
```

It proposes a command (e.g. `pytest backend-python/tests/test_task_service.py
--durations=3`). Review, then run it. **Never paste-and-run blindly** — the
suggestion is a draft.

---

## Part B — The agentic `copilot` CLI

### Step 4 — Install and start

```bash
npm install -g @github/copilot
cd labs/module-01     # or wherever your workspace root is
copilot
```

At the prompt, authenticate if asked (`/login`). Confirm it sees the repo
instructions:

```
> What engineering rules apply to this repository, and where are they defined?
```

It should cite `.github/copilot-instructions.md` and `AGENTS.md`.

### Step 5 — A scoped task in the CLI

```
> Add a `make test` target (or a cross-platform npm script in a new
  tools/ folder) that runs the Python backend tests and the frontend tests in
  sequence and exits non-zero if either fails. Follow AGENTS.md. Show me the
  diff before writing anything.
```

Review the proposed diff, approve or refine, and let it run the result. Approve
each command it wants to run individually.

### Step 6 — Non-interactive / scriptable mode

For CI or scripts, the CLI takes a single prompt and runs to completion:

```bash
copilot -p "List every endpoint in backend-python/routers/tasks.py with its method, path, and the status codes it can return. Output a Markdown table only." --allow-tool 'read'
```

Use `--allow-tool` / `--deny-tool` (and your org's policy) to constrain what a
non-interactive run may do. Keep write/exec tools off for read-only reporting.

---

## Part C — Author the CI workflow

### Step 7 — Generate it with Copilot

Back in VS Code (or continue in the `copilot` CLI). In Agent mode:

```
Create .github/workflows/ci.yml for this repo. It must:
- Trigger on push and pull_request.
- Job "backend-python": set up Python 3.12, install backend-python/requirements.txt,
  start a postgres:16 service, load database/schema.sql + seed.sql, run pytest.
- Job "frontend": set up Node 20, npm ci in frontend/, npm run build, npm test -- --run.
- Job "schema-check": start postgres:16, load schema.sql then seed.sql into a
  fresh DB, fail if either errors.
- Use official actions/* only, pinned to major versions. Cache pip and npm.
Show me the file; do not invent steps the Module 01 README doesn't support.
```

### Step 8 — Reference workflow

Your generated file should look close to this — compare and reconcile:

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  backend-python:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: postgres, POSTGRES_DB: taskboard }
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres" --health-interval 10s
          --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12", cache: pip }
      - run: pip install -r backend-python/requirements.txt
      - name: Load schema
        env: { PGPASSWORD: postgres }
        run: |
          psql -h localhost -U postgres -d taskboard -f database/schema.sql
          psql -h localhost -U postgres -d taskboard -f database/seed.sql
      - name: Test
        working-directory: backend-python
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard
        run: pytest -q

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20", cache: npm, cache-dependency-path: frontend/package-lock.json }
      - run: npm ci
        working-directory: frontend
      - run: npm run build
        working-directory: frontend
      - run: npm test -- --run
        working-directory: frontend

  schema-check:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: postgres, POSTGRES_DB: postgres }
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres" --health-interval 10s
          --health-timeout 5s --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - name: Load into a clean database
        env: { PGPASSWORD: postgres }
        run: |
          psql -h localhost -U postgres -d postgres -c "CREATE DATABASE taskboard_check;"
          psql -h localhost -U postgres -d taskboard_check -f database/schema.sql
          psql -h localhost -U postgres -d taskboard_check -f database/seed.sql
```

> Add `backend-dotnet` / `backend-java` jobs the same way if you run those —
> ask Copilot to mirror the pattern.

### Step 9 — Validate

```bash
git add .github/workflows/ci.yml && git commit -m "Add CI workflow" && git push
gh run watch          # follow the run; or: gh run list
```

Ask Copilot to explain any failure:

```bash
gh run view --log-failed | gh copilot explain -
```

(Or paste the failing step into Copilot Chat with "why did this fail and what's
the fix?".)

## Verify

- [ ] `gh copilot explain` / `suggest` work against your account.
- [ ] The `copilot` CLI runs in the repo and cites the instruction files.
- [ ] `--allow-tool 'read'` keeps a non-interactive run read-only.
- [ ] `.github/workflows/ci.yml` exists and the run is green on GitHub.
- [ ] A failing run can be explained via `gh copilot explain`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `gh copilot` not found | `gh extension install github/gh-copilot`; ensure `gh --version` ≥ 2.40. |
| `copilot` CLI auth loop | Run `/login` inside the CLI, or `gh auth login` first; check org SSO is authorised for your token. |
| CLI won't use tools | Approve tool prompts; for scripted runs pass `--allow-tool`. Org policy can disable write/exec. |
| CI: `psql` not found on runner | `ubuntu-latest` ships the Postgres client; if you changed the image, add `apt-get install -y postgresql-client`. |
| CI: frontend cache error | Set `cache-dependency-path: frontend/package-lock.json` on `setup-node`. |

## Recap — Module 02 complete

Across eight labs you added, to the Module 01 repo, a full Copilot Enterprise
customization layer:

```
labs/module-01/
├── .github/
│   ├── copilot-instructions.md          # Lab 01 — repo-wide rules
│   ├── instructions/
│   │   ├── tests.instructions.md         # Lab 01
│   │   ├── frontend.instructions.md      # Lab 01
│   │   └── code-review.instructions.md   # Lab 07
│   ├── prompts/
│   │   ├── new-endpoint.prompt.md        # Lab 02
│   │   ├── write-tests.prompt.md         # Lab 02
│   │   ├── review-diff.prompt.md         # Lab 02
│   │   └── explain-legacy.prompt.md      # Lab 02
│   ├── chatmodes/
│   │   ├── test-author.chatmode.md       # Lab 03
│   │   └── api-reviewer.chatmode.md      # Lab 03
│   ├── agents/
│   │   └── endpoint-builder.md           # Lab 03
│   ├── skills/
│   │   ├── port-endpoint/                # Lab 04 — SKILL.md + notes + scripts
│   │   └── api-contract-check/           # Lab 04 (challenge)
│   └── workflows/
│       ├── copilot-setup-steps.yml       # Lab 06
│       └── ci.yml                        # Lab 08
├── AGENTS.md                             # Lab 01
└── .vscode/
    └── mcp.json                          # Lab 05
```

This layer travels with the repo into **Module 03** (context engineering builds
on the instruction files) and **Module 04** (spec-driven development reuses the
custom chat modes and skills).
