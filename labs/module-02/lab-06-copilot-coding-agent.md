# Lab 06 — Copilot Coding Agent on GitHub.com

**Time:** ~25 min (plus agent run time) · **Surface:** GitHub.com + `gh` CLI ·
**Prereq:** Lab 03 (`endpoint-builder` agent) complete; a GitHub repo you can push to

## Objective

Push the Task Board to GitHub, configure the environment the **Copilot coding
agent** runs in, assign it a well-scoped issue, and review the pull request it
opens — all without opening an editor for the implementation.

## Why it matters for the enterprise

The coding agent is asynchronous, parallelizable delivery: small, well-specified
changes get done in the background while engineers focus on design and review.
The governance question is *"what did we let it touch, and how do we review what
it produced?"* — this lab practises both: a locked-down setup workflow, a
tightly-scoped issue, and a mandatory human PR review.

## Background

- You assign a GitHub **issue** to Copilot (or ask it to start from a PR
  comment). It runs in a GitHub Actions-powered ephemeral environment, pushes to
  a branch, and opens a **draft PR**.
- **`.github/workflows/copilot-setup-steps.yml`** — a workflow with a job named
  `copilot-setup-steps` — pre-installs tools and dependencies so the agent
  starts from a ready environment.
- The agent reads `.github/copilot-instructions.md`, `AGENTS.md`, and
  `.github/agents/*.md` — the files you built in Labs 01 and 03.
- All the agent's work lands in a PR. **Branch protection still applies.** A
  human approves before merge.

---

## Step 1 — Push the repo to GitHub

If the project isn't on GitHub yet:

**macOS / Linux / Windows (PowerShell)** — `gh` is cross-platform:

```bash
gh repo create honeywell-taskboard --private --source=. --remote=origin --push
```

Or with an existing empty remote:

```bash
git remote add origin https://github.com/<you>/honeywell-taskboard.git
git push -u origin module-02-copilot
```

Merge `module-02-copilot` into your default branch (via a PR) so the instruction
files are on `main` — the agent branches from there.

## Step 2 — Enable the coding agent

On GitHub.com: **Repository → Settings → Copilot → Coding agent** (or your
org's Copilot policy page). Confirm the coding agent is enabled for the repo.
If you don't see the option, your org admin controls it — request it.

## Step 3 — Add the setup-steps workflow

This is what makes the agent's environment able to build and test the Task
Board. Adjust to the backend you want it to work in.

```yaml
# .github/workflows/copilot-setup-steps.yml
name: Copilot setup steps

on: workflow_dispatch

jobs:
  copilot-setup-steps:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # --- Python backend ---
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Install Python deps
        working-directory: backend-python
        run: pip install -r requirements.txt

      # --- Frontend ---
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - name: Install frontend deps
        working-directory: frontend
        run: npm ci

      # --- Database for integration tests ---
      - name: Start PostgreSQL
        run: |
          docker run -d --name taskboard-db \
            -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=taskboard \
            -p 5432:5432 postgres:16
          for i in $(seq 1 30); do
            docker exec taskboard-db pg_isready -U postgres && break || sleep 1
          done
          docker exec -i taskboard-db psql -U postgres -d taskboard < database/schema.sql
          docker exec -i taskboard-db psql -U postgres -d taskboard < database/seed.sql
```

> **Add for .NET:** `actions/setup-dotnet@v4` with `dotnet-version: "8.0.x"` and
> `dotnet restore` in `backend-dotnet/`.
> **Add for Java:** `actions/setup-java@v4` (Temurin 21) and `./mvnw -B -q
> dependency:go-offline` in `backend-java/`.

Commit and push this to your default branch.

## Step 4 — Write a tightly-scoped issue

Create `ISSUE` content — keep it small, testable, and unambiguous. Via CLI:

**macOS / Linux / Windows (PowerShell)**

```bash
gh issue create --title "Add GET /api/tasks/count endpoint" --body "$(cat <<'EOF'
## Goal
Add `GET /api/tasks/count` to the **Python backend** returning:

```json
{ "count": 12 }
```

where `count` is the total number of rows in `tasks` (respecting an optional
`?status=` filter, same validation as `GET /api/tasks`).

## Constraints
- Follow `.github/copilot-instructions.md`: count query in the repository layer,
  service method calls it, router only translates HTTP.
- Unknown `?status=` value → `422`, consistent with the existing endpoint.
- No change to `database/schema.sql`.
- Add tests in `backend-python/tests/` covering: no filter, valid filter,
  invalid filter (422). `pytest` must pass.

## Use the endpoint-builder agent
EOF
)"
```

## Step 5 — Assign it to Copilot

- **GitHub.com:** open the issue → **Assignees** → select **Copilot**.
- **CLI:**

  ```bash
  gh issue edit <number> --add-assignee "@copilot"
  ```

Copilot reacts with 👀, opens a draft PR within a minute or two, and streams its
progress into the PR timeline ("session logs").

## Step 6 — Review the pull request

Wait for the agent to mark the PR **ready for review** (or review the draft).
Then, as a human reviewer:

```bash
gh pr checks <pr-number>          # did CI pass?
gh pr diff <pr-number>            # read every line
```

Check against the same list you used in Lab 05:

- [ ] Count query is in the repository, not the router.
- [ ] `422` path reuses the existing validation.
- [ ] Three tests present and passing in CI.
- [ ] `schema.sql` untouched.
- [ ] The PR description lists files changed, tests added, and test output.

If something's off, **leave a PR review comment** — the agent picks up review
comments and pushes a follow-up commit:

```bash
gh pr comment <pr-number> --body "The count query is in routers/tasks.py — move it into repositories/task_repository.py per .github/copilot-instructions.md."
```

Merge only when a human is satisfied and CI is green.

## Verify

- [ ] Repo is on GitHub with the instruction files on the default branch.
- [ ] `.github/workflows/copilot-setup-steps.yml` exists with a
      `copilot-setup-steps` job.
- [ ] Copilot opened a PR from the issue.
- [ ] The PR respects the layer rules; CI is green; you reviewed it before merge.
- [ ] (Optional) A review comment triggered a follow-up commit from the agent.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No "Copilot" assignee option | Coding agent not enabled for the repo/org — ask your admin. |
| Agent PR fails to install deps | Your `copilot-setup-steps.yml` is missing a tool. Run the workflow manually (`Actions → Copilot setup steps → Run workflow`) and read the logs. |
| Agent ignores the layer rules | Make the issue more explicit and reference `.github/agents/endpoint-builder.md` by name; re-run by re-assigning. |
| Agent scope creep | The issue was too broad. Close the PR, split the issue, retry. Small issues = good agent results. |
| CI not running on the agent's PR | Branch/workflow permissions — ensure Actions run on PRs from the agent's branch. |

## Recap & carry-forward

You delegated a change end-to-end and gated it with human review. **Lab 07**
adds the other half of the loop: automated Copilot review on every PR, including
this one.
