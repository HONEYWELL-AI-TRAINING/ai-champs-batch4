# Lab 01 — Fork, Clone, Build & Run the Task Board

**Time:** ~40 min · **Surface:** GitHub.com + terminal ·
**Prereq:** a GitHub account with access to the programme's Copilot licence;
tools from the [README prerequisites](README.md#prerequisites)

## Objective

Create your **own fork** of
[`HONEYWELL-AI-TRAINING/honeywell-taskboard`](https://github.com/HONEYWELL-AI-TRAINING/honeywell-taskboard),
clone it, then build, test, and run the whole stack — PostgreSQL, one backend,
and the React board — and push a first branch back to your fork.

By the end you have a working copy of the Task Board that **every later lab in
the programme uses as its workspace**.

## Why it matters for the enterprise

Module 02 onward is not just "edit files locally". The coding agent, Copilot
code review, pull-request automation, and Actions all act on a repository **on
GitHub.com** — so you need a repo you can push to, open pull requests in, and
break safely without touching the shared original. A fork gives each AI Champion
exactly that, while keeping a link back to the upstream so you can pull in fixes.

It is also the first step of the brownfield habit the programme teaches: you
start from an existing, tested codebase and prove it is green **before** you
change anything. That "known-good" run is the baseline for everything after.

## Background

- **Upstream** — `HONEYWELL-AI-TRAINING/honeywell-taskboard` (public, default
  branch `main`). Read-only for you.
- **Fork (`origin`)** — your copy, under your account. You push here.
- **Clone** — the working copy on your machine.

```
 upstream (HONEYWELL-AI-TRAINING)  ──fork──▶  origin (your account)  ──clone──▶  your machine
              ▲                                                                       │
              └───────────── git fetch upstream (pull in updates) ◀───────────────────┘
```

> **The fork is richer than the Module 01 starting point.** Its `main` branch
> already contains the finished *task comments* feature (`task_comments` table,
> `/api/tasks/{id}/comments`, a comments UI), a Copilot customization layer
> (`.github/copilot-instructions.md`, `instructions/`, `prompts/`, `agents/`,
> `skills/`), and the Spec Kit artifacts (`.specify/`, `specs/001-task-comments/`).
> That is why its test counts are higher than the ones in the
> [README checklist](README.md#verification). Do **not** delete any of it. Where
> a later lab says "create X" and X already exists, compare yours with the
> existing one, or ask your facilitator which to use.

---

## Step 1 — Check your tools

Run these in any shell. You need Git, Node, and **at least one** backend toolchain
plus PostgreSQL or Docker. Versions are the ones the repo needs.

```
git --version        # any recent
node --version       # 20.19+ or 22.12+
npm --version
docker --version     # or have PostgreSQL 15+ installed locally
python3 --version    # 3.11+   (Windows: python --version)  — Python backend
dotnet --version     # 8.0+                                 — .NET backend
java -version        # 21+                                  — Java backend
```

Optional but recommended: the GitHub CLI (`gh --version`,
[cli.github.com](https://cli.github.com)). The steps below show the web UI and
the `gh` way side by side — use either.

Set your Git identity once if you have not (use the email tied to your GitHub
account):

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

## Step 2 — Fork the repository

### Option A — GitHub web UI

1. Open <https://github.com/HONEYWELL-AI-TRAINING/honeywell-taskboard> while signed in.
2. Click **Fork** (top right) → **Create a new fork**.
3. **Owner:** your personal account (or the account/organisation your
   facilitator tells you to use). **Repository name:** keep
   `honeywell-taskboard`. Leave **Copy the `main` branch only** ticked.
4. Click **Create fork**. You land on
   `https://github.com/<your-username>/honeywell-taskboard`.

### Option B — GitHub CLI (fork and clone in one go)

```
gh auth login
gh repo fork HONEYWELL-AI-TRAINING/honeywell-taskboard --clone
```

This forks, clones into `./honeywell-taskboard`, and adds an `upstream` remote
for you. If you used this option, skip to **Step 4**.

> **Cannot fork?** If the Fork button is greyed out or creation fails, your
> account is likely an Enterprise Managed User (EMU) account, which cannot fork
> into a personal namespace. Ask your facilitator which organisation to fork into
> (or for a repo to be created for you from the same source).

## Step 3 — Clone your fork

Pick a folder **outside** any other Git repository (not inside this course
repo), then clone *your fork* — not the upstream:

```
git clone https://github.com/<your-username>/honeywell-taskboard.git
cd honeywell-taskboard
```

Replace `<your-username>` with your GitHub username. The commands are the same
on macOS, Linux, and Windows (PowerShell).

> **Sign-in prompts.** HTTPS pushes need a credential. The easiest route is
> `gh auth login` followed by `gh auth setup-git`; otherwise use the Git
> Credential Manager (installed with Git for Windows / macOS) and a personal
> access token as the password. Passwords for your GitHub account do not work.

## Step 4 — Add the upstream remote

```
git remote add upstream https://github.com/HONEYWELL-AI-TRAINING/honeywell-taskboard.git
git remote -v
```

Expected: `origin` points at **your** fork and `upstream` at
`HONEYWELL-AI-TRAINING`, each listed for fetch and push.

To pull in upstream changes later (do this when the facilitator announces an
update, not mid-lab):

```
git switch main
git fetch upstream
git merge --ff-only upstream/main
git push origin main
```

(`gh repo sync <your-username>/honeywell-taskboard` does the same on GitHub's side.)

## Step 5 — Orient yourself (5 min)

```
git log --oneline -3
```

Open these in your editor — they are the "map" every AI-assisted change starts from:

| File / folder | What it tells you |
|---------------|-------------------|
| `README.md` | Architecture, ports, config, run and test commands |
| `AGENTS.md` and `.github/copilot-instructions.md` | The engineering rules (three layers, schema ownership, error contract, tests-first) |
| `docs/usecase.md` | Domain, data model, API contract |
| `database/schema.sql` | The only place the schema is defined |
| `backend-python/`, `backend-dotnet/`, `backend-java/` | Three interchangeable backends behind one API |
| `frontend/` | React + Vite board |

## Step 6 — Start the database

You need PostgreSQL with a database called `taskboard`. The simplest route is
Docker (one command, identical in every shell):

```
docker run --name taskboard-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=taskboard -p 5432:5432 -d postgres:16
```

Now apply the schema and seed data from the repo root.

**macOS / Linux**

```bash
docker exec -i taskboard-db psql -U postgres -d taskboard < database/schema.sql
docker exec -i taskboard-db psql -U postgres -d taskboard < database/seed.sql
```

**Windows (PowerShell)** — `<` redirection is not supported, so pipe instead:

```powershell
Get-Content database/schema.sql | docker exec -i taskboard-db psql -U postgres -d taskboard
Get-Content database/seed.sql   | docker exec -i taskboard-db psql -U postgres -d taskboard
```

**Using a local PostgreSQL instead of Docker** (any platform; create the
`taskboard` database first):

```
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -f database/schema.sql
psql "postgresql://postgres:postgres@localhost:5432/taskboard" -f database/seed.sql
```

Check it loaded:

```
docker exec taskboard-db psql -U postgres -d taskboard -c "SELECT count(*) FROM tasks;"
```

Expected: `6`. `seed.sql` is safe to re-run — it truncates and reloads the sample
tasks, which is how you reset the board between exercises.

> The commands use the local-dev default password `postgres`. If you chose a
> different password, use it in every connection string below.

## Step 7 — Build and test (prove it is green first)

None of the backend tests need the database. Run them for the backend(s) you
plan to use, plus the frontend. Run each block from its folder, starting at the
repo root.

**Python — `backend-python/`**

```bash
cd backend-python
python3 -m venv .venv && source .venv/bin/activate   # Windows: python -m venv .venv ; .venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
cd ..
```

**.NET — `backend-dotnet/`**

```
cd backend-dotnet
dotnet build
dotnet test
cd ..
```

**Java — `backend-java/`**

```bash
cd backend-java
./mvnw -B test            # Windows: .\mvnw.cmd -B test
cd ..
```

**Frontend — `frontend/`**

```
cd frontend
npm install
npm run build
npm test -- --run
cd ..
```

Expected results on a fresh fork (verified against upstream commit `c38a6f1`):

| Suite | Passing tests |
|-------|---------------|
| Python (`pytest`) | 52 |
| .NET (`dotnet test`) | 25 |
| Java (`./mvnw test`) | 27 |
| Frontend (`npm test -- --run`) | 20 |

If upstream has moved on since this was written, the numbers may be higher — what
matters is **zero failures**. If anything fails, stop and fix it now (see
[Troubleshooting](#troubleshooting)); do not start later labs on a red baseline.

## Step 8 — Run a backend

Pick **one** (use a second one later for the cross-backend exercises). Run from
the repo root; each backend keeps its terminal busy, so give it its own window.

### Option A — Python (FastAPI), port 8000

```bash
cd backend-python
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
```
```bash
# macOS / Linux
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard"
```
```powershell
# Windows (PowerShell)
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/taskboard"
```
```
uvicorn main:app --reload
```
API docs: <http://localhost:8000/docs>

### Option B — .NET (ASP.NET Core), port 5088

```bash
cd backend-dotnet
```
```bash
# macOS / Linux
export ConnectionStrings__DefaultConnection="Host=localhost;Port=5432;Database=taskboard;Username=postgres;Password=postgres"
```
```powershell
# Windows (PowerShell)
$env:ConnectionStrings__DefaultConnection = "Host=localhost;Port=5432;Database=taskboard;Username=postgres;Password=postgres"
```
```
dotnet run --project src/TaskBoard.Api
```
API docs: <http://localhost:5088/swagger>

### Option C — Java (Spring Boot), port 8080

```bash
cd backend-java
```
```bash
# macOS / Linux
export SPRING_DATASOURCE_URL="jdbc:postgresql://localhost:5432/taskboard"
export SPRING_DATASOURCE_USERNAME=postgres
export SPRING_DATASOURCE_PASSWORD=postgres
./mvnw spring-boot:run
```
```powershell
# Windows (PowerShell)
$env:SPRING_DATASOURCE_URL = "jdbc:postgresql://localhost:5432/taskboard"
$env:SPRING_DATASOURCE_USERNAME = "postgres"
$env:SPRING_DATASOURCE_PASSWORD = "postgres"
.\mvnw.cmd spring-boot:run
```
API docs: <http://localhost:8080/swagger-ui.html>

### Smoke-test the API

In a new terminal (swap the port for your backend: `8000` Python, `5088` .NET,
`8080` Java).

**macOS / Linux**

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/tasks
```

**Windows (PowerShell)** — `curl` is an alias for `Invoke-WebRequest` in Windows
PowerShell 5.1, so call the real binary:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/api/tasks
```

Expected: `{"status":"ok"}` and a JSON array of the six seeded tasks.

## Step 9 — Run the frontend

Point the frontend at the backend you started. The template is
`frontend/.env.example`; `.env.local` is git-ignored.

**macOS / Linux**

```bash
cd frontend
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

**Windows (PowerShell)** — force UTF-8 so Vite reads it correctly:

```powershell
cd frontend
Set-Content -Encoding utf8 .env.local "VITE_API_BASE_URL=http://localhost:8000"
```

Use `:5088` for .NET or `:8080` for Java instead of `:8000`. Then:

```
npm run dev            # http://localhost:5173
```

Open <http://localhost:5173> and confirm:

- [ ] The board shows the six seeded tasks across **To Do / In Progress / Done**
- [ ] You can create a task, move it between columns, and delete it
- [ ] The status filter narrows the list
- [ ] You can open a task's comments and add one

> Vite reads `.env.local` only at startup. If you change the backend URL, stop
> the dev server (`Ctrl+C`) and run `npm run dev` again.

## Step 10 — Push your first branch to the fork

Prove your fork is wired up end to end. From the repo root:

```
git switch -c module-01/fork-check
git commit --allow-empty -m "Lab 01: fork verified"
git push -u origin module-01/fork-check
```

Open `https://github.com/<your-username>/honeywell-taskboard/branches` and
confirm `module-01/fork-check` is listed under **your** fork.

> **Pull requests from a fork default to the *upstream* repo.** Whenever a later
> lab has you open a PR, set **base repository** to
> `<your-username>/honeywell-taskboard` (`base: main`) — not
> `HONEYWELL-AI-TRAINING/...`. With the CLI use
> `gh pr create --repo <your-username>/honeywell-taskboard`. You do not have
> permission to, and must not, open PRs against the upstream.

Then return to `main` so you start later labs from a clean tree:

```
git switch main
```

## Using the fork in later modules

- **Workspace root = the fork root.** Open the `honeywell-taskboard` folder
  itself in VS Code (`code .`). Wherever another lab says `labs/module-01/`,
  use the root of your fork. This also puts `.github/` directly under the
  workspace root, where Copilot looks for instructions, prompts, agents, and skills.
- **Same commands, same paths.** The folder names (`backend-python/`,
  `frontend/`, `database/` …) and layering match the Module 01 README, so its
  [Exercises](README.md#exercises) work unchanged on your fork — do them on
  branches, as the README suggests.
- **GitHub.com features act on your fork.** The Copilot coding agent, Copilot
  code review, and Actions in Module 02 run against `origin`. Make sure
  Copilot is enabled for your account/organisation; your facilitator will
  confirm any repository-level settings.
- **Daily start-up**, once everything is installed:

  ```
  docker start taskboard-db          # database
  # then your backend (Step 8) and `npm run dev` in frontend/ (Step 9)
  ```

  Stop with `Ctrl+C` in each terminal and `docker stop taskboard-db`. To wipe the
  database entirely: `docker rm -f taskboard-db`, then redo Step 6.

## Verification

- [ ] `git remote -v` shows `origin` = your fork and `upstream` = `HONEYWELL-AI-TRAINING/honeywell-taskboard`
- [ ] `SELECT count(*) FROM tasks;` returns `6`
- [ ] Tests pass for your backend(s) and the frontend (zero failures)
- [ ] `/health` returns `{"status":"ok"}` and `/api/tasks` returns the seeded tasks
- [ ] The board at <http://localhost:5173> renders and CRUD works against the live backend
- [ ] `module-01/fork-check` is visible on **your** fork on GitHub
- [ ] No secrets committed (`.env*` files stay untracked — check `git status`)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Fork button disabled / "cannot fork" | EMU or organisation policy — ask your facilitator which organisation to fork into (Step 2). |
| `remote: Permission denied` / `403` on push | You cloned the **upstream**, not your fork. Check `git remote -v`; fix with `git remote set-url origin https://github.com/<your-username>/honeywell-taskboard.git`. |
| `Authentication failed` on push | Passwords are not accepted. Run `gh auth login` then `gh auth setup-git`, or use a personal access token (Step 3). |
| `port is already allocated` / `address already in use` on 5432 | A local PostgreSQL is running. Stop it, or map Docker to another port (`-p 5433:5432`) and use `5433` in every connection string. |
| `password authentication failed for user "postgres"` | The password in your connection string differs from `POSTGRES_PASSWORD`. If the container already existed, `docker rm -f taskboard-db` and redo Step 6. |
| `database "taskboard" does not exist` (local PostgreSQL) | Create it first: `createdb -U postgres taskboard`, then reapply the schema. |
| `relation "tasks" does not exist` at runtime | Schema was not applied — redo the `schema.sql` command in Step 6. No backend creates tables itself. |
| Board is empty or shows a network / CORS error | Wrong `VITE_API_BASE_URL` for the running backend, or the backend is not up. Fix `.env.local`, restart `npm run dev`, and re-check `/health`. |
| `externally-managed-environment` from `pip` | You are outside the virtualenv. Create and activate `.venv` (Step 7). |
| PowerShell: `running scripts is disabled` on `Activate.ps1` | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again. |
| `./mvnw: Permission denied` | `chmod +x backend-java/mvnw` (macOS / Linux). Windows uses `mvnw.cmd`. |
| `No .NET SDKs were found` / wrong Java version | Install .NET SDK 8+ / JDK 21+ and reopen the terminal so `PATH` refreshes. |
| `Unsupported engine` / Vite refuses to start | Node is too old — upgrade to 20.19+ or 22.12+. |
| A test fails on a fresh fork | Re-run it once, then capture the output and raise it with your facilitator. Do not edit tests to make them pass. |

---

**Next:** return to the [Module 01 README](README.md#exercises) and run the
workshop Exercises on your fork, then continue to [Module 02](../module-02/README.md).
