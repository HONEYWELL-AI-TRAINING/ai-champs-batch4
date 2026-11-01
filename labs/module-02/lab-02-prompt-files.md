# Lab 02 — Reusable Prompt Files (Team Slash-Commands)

**Time:** ~20 min · **Surface:** VS Code (primary); JetBrains support is rolling out ·
**Prereq:** Lab 01 complete

## Objective

Turn the repetitive requests your team makes of Copilot — "scaffold an
endpoint", "write tests for this", "review my diff against our rules" — into
**checked-in prompt files** that anyone runs as a slash-command: `/new-endpoint`,
`/write-tests`, `/review-diff`.

## Why it matters for the enterprise

A prompt file is a **standardized, versioned workflow**. Instead of ten
engineers writing ten slightly different "add an endpoint" prompts (and getting
ten slightly different results), everyone runs the same reviewed prompt. When
the team learns something — "always ask it to check the error contract" — you
change one file in a PR and everyone benefits.

## Background

- Prompt files live in `.github/prompts/NAME.prompt.md`.
- In Copilot Chat you invoke one by typing `/NAME`.
- Frontmatter controls how it runs:

  | Key | Purpose |
  |-----|---------|
  | `description` | Shown in the slash-command picker |
  | `mode` | `ask`, `edit`, or `agent` |
  | `model` | Optional — pin a model (e.g. a reasoning model for reviews) |
  | `tools` | Optional — which agent tools the prompt may use |

- Body variables: `${input:name}` / `${input:name:placeholder}` prompt the user
  for a value; `${selection}` is the selected code; `${file}` the current file;
  `${workspaceFolder}` the root. You can also reference files with Markdown
  links like `[the contract](../../usecase.md)`.

---

## Step 1 — Create the prompts folder

**macOS / Linux**

```bash
mkdir -p .github/prompts
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force -Path .github\prompts | Out-Null
```

## Step 2 — `/new-endpoint` — scaffold a feature across all three layers

```md
<!-- .github/prompts/new-endpoint.prompt.md -->
---
description: Scaffold a new Task Board endpoint across router, service, repository, and tests
mode: agent
---
Add a new endpoint to the **currently open backend** only.

Endpoint: `${input:method:HTTP method, e.g. GET}` `${input:path:route, e.g. /api/tasks/count}`
Behaviour: ${input:behaviour:what it should do}

Follow `.github/copilot-instructions.md` exactly:
1. Start with the **repository** method (all DB access here).
2. Add the **service** method that calls it (validation / rules here).
3. Add the **controller/router** handler (HTTP translation + error mapping only).
4. Add or update tests in the matching test file FIRST-class, covering the happy
   path plus `404` / `422` where they apply.
5. Do not touch `database/schema.sql` unless I explicitly ask for a schema change.

After editing, run the backend's test command and report the result. Show me
the full diff before I accept.
```

## Step 3 — `/write-tests` — cover the selected code

```md
<!-- .github/prompts/write-tests.prompt.md -->
---
description: Generate tests for the selected code following the suite's conventions
mode: agent
---
Write tests for this code:

```
${selection}
```

From file: ${file}

Requirements:
- Put them in the existing test file for this module; match its framework,
  imports, and naming (see `.github/instructions/tests.instructions.md`).
- Cover: happy path, boundary/empty input, and every error branch in the code
  above (especially `404` and `422`).
- Use the existing fixtures / fakes — do not connect to a real database.
- Run the suite and paste the summary line. If anything fails, fix the test,
  not the source, unless the source is clearly wrong — then flag it.
```

## Step 4 — `/review-diff` — check uncommitted work against the house rules

```md
<!-- .github/prompts/review-diff.prompt.md -->
---
description: Review the current git diff against the Task Board engineering rules
mode: agent
tools: ['changes', 'search', 'runCommands']
---
Review my **uncommitted changes** (`git diff HEAD`) against
`.github/copilot-instructions.md`.

Report, as a short checklist:
- Layer violations (SQL in a controller, validation in a repository, etc.)
- Schema-ownership violations (migrations, `create_all`, `ddl-auto`)
- Error-contract violations (wrong or invented status codes)
- Missing or weak tests for changed behaviour
- Cross-backend drift: would this change be portable to the other two backends?

For each issue: the file, the line, and the smallest fix. If the diff is clean,
say so and stop. Do not make changes — this is review only.
```

## Step 5 — `/explain-legacy` — onboard to an unfamiliar area

```md
<!-- .github/prompts/explain-legacy.prompt.md -->
---
description: Explain how a Task Board feature works end to end, for someone new to the file
mode: ask
---
Explain `${input:feature:feature or endpoint, e.g. PUT /api/tasks/{id}}` end to end.

Trace it through every layer from the React `services/` call (if the UI uses it)
down to the `tasks` table and back. For each hop name the file and the function.
Call out: where validation happens, where errors are mapped to status codes,
and any assumption in the code that a change could break.
Keep it under 250 words. Do not suggest changes.
```

## Step 6 — Run them

1. Reload VS Code so it picks up the new prompt files
   (Command Palette → **Developer: Reload Window**).
2. Open a backend file (say `backend-python/routers/tasks.py`).
3. In Copilot Chat, type `/` — your four prompts appear in the picker with
   their descriptions.
4. Run `/explain-legacy` with feature `GET /api/tasks?status=` and read the
   trace. This is the **Code Explanation** capability from the Module 02
   concept guide, made repeatable.
5. Select the `list_tasks` function body, run `/write-tests`, review the diff,
   and run the suite:

   **macOS / Linux**

   ```bash
   cd backend-python && pytest -q
   ```

   **Windows (PowerShell)**

   ```powershell
   cd backend-python ; pytest -q
   ```

6. Make a small deliberate mistake (e.g. add a `raise HTTPException(400, ...)`
   somewhere), then run `/review-diff` and confirm it flags the `400` as an
   error-contract violation. Revert the mistake.

## Step 7 — Commit

```bash
git add .github/prompts && git commit -m "Add reusable Copilot prompt files"
```

## Verify

- [ ] Four files exist under `.github/prompts/`.
- [ ] Typing `/` in Copilot Chat lists all four with descriptions.
- [ ] `/write-tests` produces tests in the *existing* test file using the
      suite's framework (not a new ad-hoc file).
- [ ] `/review-diff` catches an intentional `400` status code.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Slash-commands don't appear | Reload the window. Confirm files end in `.prompt.md` and sit in `.github/prompts/`. |
| `${input:...}` not prompting | Check the syntax — `${input:name:placeholder}`, no spaces around the colons. |
| Prompt ignores the house rules | Prompt files do **not** auto-include `copilot-instructions.md` verbatim in older builds — reference it explicitly in the body, as these do. |
| `tools:` key rejected | Your Copilot version may use a different tool-set syntax; remove the line — the prompt still runs, just without the tool restriction. |

## Recap & carry-forward

You have a team slash-command library. **Lab 03** wraps a *persona* around
these — a custom chat mode that always reviews, or always writes tests, with a
constrained tool set and its own model.
