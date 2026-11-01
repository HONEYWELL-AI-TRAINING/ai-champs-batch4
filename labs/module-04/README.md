# Module 04 — Spec-Driven Development with GitHub Spec Kit (Hands-On Lab)

## What this lab is

Module 04 builds **one genuinely new feature** on the Module 01 Task Board —
**task comments** — the spec-driven way, using **GitHub Spec Kit**. No new app.
You keep the Module 01 codebase and the Module 02 / 03 customization layer
(`.github/copilot-instructions.md`, prompt files, chat modes, skills,
`/context-brief`, `CONTEXT.md`) and add the Spec Kit artifact set on top:
`constitution.md → spec.md → plan.md → tasks.md → implementation → validation`.

| Lab | SDD phase | Spec Kit commands | You produce |
|-----|-----------|-------------------|-------------|
| [01](lab-01-constitution-and-spec.md) | Principles + specification | `/speckit.constitution`, `/speckit.specify`, `/speckit.clarify` | `.specify/memory/constitution.md`, `specs/001-task-comments/spec.md` |
| [02](lab-02-plan-and-tasks.md) | Architecture + work breakdown | `/speckit.plan`, `/speckit.tasks`, `/speckit.analyze` | `plan.md`, `tasks.md`, a REQ→TASK trace |
| [03](lab-03-implement-and-validate.md) | Implementation + acceptance | `/speckit.implement` (+ Module 02/03 tools) | working, tested feature; filled acceptance checklist |
| [04](lab-04-traceability-and-change-control.md) | Change control + prompt-only comparison | spec edit → re-`/plan` → re-`/tasks` → `/implement` | final traceability matrix; comparison notes |

Work through them in order. Total time: about **2 hours**.

## The feature you will build

The plain-English brief every lab starts from is in
**[feature-brief.md](feature-brief.md)** — read it once now. In short:

> Engineers can leave short **comments** on a task (an activity thread). New
> table `task_comments`; `GET` / `POST` / `DELETE` under
> `/api/tasks/{id}/comments`; a comment count badge and an expandable thread on
> the board. Same layering, error contract, and cross-backend parity rules as
> the rest of the app.

This is deliberately a feature that a one-line prompt gets *wrong* — comment
ordering, the character limits, the `404` vs `422` split, the schema change, the
UI states — which is exactly what a specification is for.

## Prerequisites

- **Modules 01–03 completed.** Task Board runs locally; the `.github/` layer and
  `CONTEXT.md` from Modules 02–03 are on your branch.
- [Module 01 prerequisites](../setup/prerequisites.md) + a working backend,
  frontend, and database.
- **GitHub Copilot** signed in inside VS Code (Spec Kit drives Copilot Chat).
- **`uv`** (or `pipx`) for the `specify` CLI — [docs.astral.sh/uv](https://docs.astral.sh/uv/).
  Check with `uv --version`.
- Internet access for `specify init` (it fetches templates). An offline fallback
  is noted in Lab 01.

## Platform conventions

Shell blocks are given for **macOS / Linux (bash/zsh)** and **Windows
(PowerShell)**. WSL2 users follow the macOS / Linux side. When you run
`specify init` you pick a script type — choose **sh** on macOS/Linux/WSL,
**ps** on native Windows PowerShell. Copilot Chat slash-commands are identical
on every OS.

## Set-up — do this once before Lab 01

### 1. Open the Task Board as the workspace root

**macOS / Linux**

```bash
cd labs/module-01
code .
```

**Windows (PowerShell)**

```powershell
cd labs\module-01
code .
```

All paths in these labs (`.specify/…`, `specs/…`, `.github/…`) are **inside
`labs/module-01/`**.

### 2. Branch from your Module 03 work

```bash
git checkout module-03-context      # or wherever Module 03 landed
git checkout -b module-04-sdd
```

### 3. Install the `specify` CLI

**macOS / Linux**

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify --version
```

**Windows (PowerShell)**

```powershell
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify --version
```

No-install alternative (runs it once): `uvx --from git+https://github.com/github/spec-kit.git specify init …`

### 4. Sanity-check

```bash
specify check
```

It reports whether Copilot, Git, and the script tools it needs are available.

You are ready. Start with [Lab 01](lab-01-constitution-and-spec.md).

## How each lab is structured

Objective → Why it matters for the enterprise → Background → Steps (both
platforms) → Files/templates → Verify → Troubleshooting → Recap & carry-forward.

## A note on Spec Kit's pace of change

Spec Kit is young and moves fast. Command names in these labs use the current
`/speckit.<name>` form; older installs use bare `/<name>` (e.g. `/specify`).
Artifact file names and folder layout may shift — `specify --help` and the
[Spec Kit docs](https://github.github.com/spec-kit/) are the source of truth.
The *method* — constitution → spec → plan → tasks → implement, with change
control flowing back through the spec — is stable and is what this module
teaches.

## After this module

- The Task Board repo carries a full, versioned spec for the comments feature.
- **Module 05** takes this same spec through the complete SDLC, greenfield and
  brownfield.
- **Module 06** derives its test strategy directly from the acceptance criteria
  you write in Lab 01.
