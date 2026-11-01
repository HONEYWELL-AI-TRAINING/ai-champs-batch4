# Lab 01 — Repository & Path-Specific Custom Instructions

**Time:** ~25 min · **Surface:** VS Code / JetBrains / Visual Studio / GitHub.com ·
**Prereq:** Module 02 [set-up](README.md#set-up--do-this-once-before-lab-01) done

## Objective

Make every engineer's Copilot follow the **same** Task Board rules — 3-layer
architecture, single schema owner, error contract — without anyone typing those
rules into chat. You will add a repository-wide instruction file and two
path-scoped instruction files, then prove Copilot obeys them.

## Why it matters for the enterprise

Prompt-only development gives inconsistent results because every engineer
carries different context in their head. A checked-in instruction file turns
"what good looks like here" into **version-controlled, reviewable configuration**
that applies to Copilot Chat, inline suggestions, agent mode, Copilot code
review, and the coding agent — everywhere, for everyone, automatically.

## Background — the three instruction mechanisms

| File | Scope | Loaded when |
|------|-------|-------------|
| `.github/copilot-instructions.md` | Whole repository | Every Copilot request in this repo |
| `AGENTS.md` (repo root) | Whole repository | Same; recognised by Copilot coding agent, Copilot CLI, and other agents |
| `.github/instructions/NAME.instructions.md` | Files matching an `applyTo` glob | Only when the request touches matching files |

`.github/copilot-instructions.md` and `AGENTS.md` overlap. Use
`copilot-instructions.md` as the primary file for IDE Copilot; add a short
`AGENTS.md` that points at it so command-line and third-party agents pick up the
same rules.

---

## Step 1 — Create the repository instruction file

VS Code has a helper: open the Command Palette (`Ctrl`/`Cmd`+`Shift`+`P`) →
**Chat: New Instructions File** → scope *Workspace*. Or just create the file by
hand.

**macOS / Linux**

```bash
mkdir -p .github
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force -Path .github | Out-Null
```

Create the file:

```md
<!-- .github/copilot-instructions.md -->
# Engineering Task Board — Copilot Instructions

## What this project is
A Kanban task board: PostgreSQL + a React frontend + ONE backend (.NET, Python,
or Java) behind a shared REST contract. Domain is deliberately small; the point
is disciplined full-stack change.

## Architecture — do not violate
Every backend uses the same three layers. Keep responsibilities where they belong:

| Layer | Allowed to do | Never does |
|-------|---------------|------------|
| Controller / Router | Translate HTTP <-> domain, map errors to status codes | Business rules, SQL |
| Service | Validation, business rules | HTTP concerns, SQL |
| Repository | ALL database access | Validation, HTTP concerns |

The React app layers the same way: `components/` (presentational) → `pages/`
(state + data fetching) → `services/` (all HTTP in one place).

## Hard rules
- **Schema is owned once**, in `database/schema.sql`. Do NOT add EF migrations,
  `Base.metadata.create_all()`, or `ddl-auto` values other than `none`.
- `created_at` / `updated_at` are set by the database, never by the client.
- `status` is exactly one of: `todo`, `in-progress`, `done`.
- Error contract: `404` for a missing id; `422` for a missing title or an
  unknown status. Do not invent other codes.
- Any new endpoint gets a test in the same layer BEFORE the implementation is
  considered done.

## Conventions
- Match the existing style of the file you are editing; do not reformat
  untouched lines.
- Keep the three backends behaviourally identical — a change to one should be
  portable to the others with the same request/response shape.
- Prefer editing an existing file over creating a new one.

## How to verify a change
- .NET: `dotnet test` in `backend-dotnet/`
- Python: `pytest` in `backend-python/`
- Java: `./mvnw -B test` in `backend-java/`
- Frontend: `npm test -- --run` in `frontend/`
```

> **JetBrains / Visual Studio:** the same `.github/copilot-instructions.md`
> file is read automatically. In VS Code, confirm the setting
> **`github.copilot.chat.codeGeneration.useInstructionFiles`** is enabled
> (it is on by default in current versions).

## Step 2 — Add `AGENTS.md` for command-line and third-party agents

```md
<!-- AGENTS.md -->
# Agent Instructions

The authoritative engineering rules for this repository are in
[`.github/copilot-instructions.md`](.github/copilot-instructions.md).
Read that file first and follow it exactly.

## Quick reference
- Three layers: Controller/Router → Service → Repository. No layer-skipping.
- Schema is owned only by `database/schema.sql`. No migrations.
- Error contract: 404 missing id, 422 missing title / unknown status.
- Add or update a test before considering an endpoint change done.

## Build & test
- Backend (.NET): `cd backend-dotnet && dotnet test`
- Backend (Python): `cd backend-python && pytest`
- Backend (Java): `cd backend-java && ./mvnw -B test`
- Frontend: `cd frontend && npm test -- --run`
```

## Step 3 — Add path-specific instructions for tests

These apply **only** when Copilot is working on test files, so the main
instruction file stays short.

```md
<!-- .github/instructions/tests.instructions.md -->
---
applyTo: "**/*{test,Test,tests,Tests,_test}*.{cs,py,js,jsx,java}"
---
# Writing tests for the Task Board

- Mirror the structure of the neighbouring existing test file — same framework,
  same naming, same arrange/act/assert rhythm.
  - .NET: xUnit + `WebApplicationFactory` for controller tests.
  - Python: pytest + `httpx.AsyncClient` against the FastAPI app.
  - Java: JUnit 5 + `@SpringBootTest` / `MockMvc`.
  - Frontend: Vitest + Testing Library.
- Every endpoint test covers: the happy path, `404` for a missing id, and
  `422` for a missing title or an unknown status.
- Do not hit a real database — use the existing in-memory / fixture setup from
  `conftest.py`, the test factory, or the repository fake already in the suite.
- Name tests for the behaviour, not the method: `returns_422_when_title_missing`.
```

## Step 4 — Add path-specific instructions for the frontend

```md
<!-- .github/instructions/frontend.instructions.md -->
---
applyTo: "frontend/**"
---
# Frontend conventions

- All HTTP goes through `src/services/` — components and pages never call
  `fetch` directly.
- Components in `src/components/` are presentational: props in, callbacks out,
  no data fetching.
- Status values and column labels come from `src/constants.js`. Do not hard-code
  the strings `todo` / `in-progress` / `done` in components.
- Keep the existing plain-CSS approach in `index.css`; do not add a CSS
  framework or styling library.
```

## Step 5 — Prove Copilot follows the instructions

1. Commit what you have so the diff for the next step is clean:

   ```bash
   git add .github AGENTS.md && git commit -m "Add Copilot instruction layer"
   ```

2. Open Copilot Chat, set it to **Ask** mode, and send:

   ```
   Add a GET /api/tasks/count endpoint that returns { "count": <number of tasks> }.
   Tell me which files you would change and why, but do not write code yet.
   ```

3. **Check the answer against the instructions.** A correct plan will:
   - put the count query in the **repository**, not the controller;
   - add a **service** method that calls it;
   - add a **test** first (in the file `tests.instructions.md` points at);
   - *not* mention a migration or schema change.

   If the plan skips a layer or offers to "just add it to the controller for
   simplicity", the instruction file is not being read — see Troubleshooting.

4. Now do the same request in a fresh chat **with the `count` in a Java context**
   (open a `backend-java` file first) and confirm the plan switches to
   JUnit / Spring conventions from the path instructions.

## Verify

- [ ] `.github/copilot-instructions.md`, `AGENTS.md`, and two files under
      `.github/instructions/` exist and are committed.
- [ ] VS Code: hovering the "References" line under a Copilot Chat response
      lists `copilot-instructions.md` as an included instruction file. (In
      current VS Code, used instruction files show in the response's
      *References* / *Used N references* disclosure.)
- [ ] The Step 5 plan respects the layer boundaries and asks for a test first.
- [ ] Opening a Java file changes the test framework Copilot proposes.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Instructions seem ignored | Confirm the workspace root is `labs/module-01/` (not the repo root), so `.github/` is directly under it. Reload the window. |
| VS Code | Check `github.copilot.chat.codeGeneration.useInstructionFiles` is `true` in Settings. |
| Path instructions never apply | The `applyTo` glob must match the *relative* path from the workspace root. Test your glob against an actual filename. |
| Too many instructions, responses get vague | Keep `copilot-instructions.md` under ~1 page. Move detail into `applyTo`-scoped files so it loads only when relevant. |

## Recap & carry-forward

You now have a reviewable Copilot configuration layer in the repo. **Lab 02**
adds reusable prompts that reference these same rules; **Lab 07** shows the
instruction file also drives automated Copilot code review on pull requests.
