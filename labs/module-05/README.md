# Module 05 — SDD to a Complete SDLC: Greenfield & Brownfield (Hands-On Lab)

## What this lab is

Module 04 took a specification as far as a validated feature. Module 05 walks
**every stage of the SDLC — twice**: once carrying that greenfield feature all
the way to **release-ready**, and once applying the same discipline to a
**brownfield** change that evolves existing behaviour without breaking it. Same
Task Board codebase, same Spec Kit tooling, same `.github/` layer from Modules
02–04. No new app.

| Lab | Track | You produce |
|-----|-------|-------------|
| [01](lab-01-greenfield-spec-to-release.md) | **Greenfield** — carry the comments spec to release-ready | integration tests, extended CI with quality gates, `release-readiness.md` |
| [02](lab-02-brownfield-archaeology-and-impact.md) | **Brownfield** — understand before you touch | `archaeology.md`, `change-impact.md` (blast radius), a scoped spec + plan |
| [03](lab-03-brownfield-implement-and-compare.md) | **Brownfield** — minimal change + regression protection, then compare | the change implemented in-scope, `regression-report.md`, `greenfield-vs-brownfield.md` |

Work through them in order. Total time: about **3 hours** (the deck budgets 4
for the full workshop including discussion).

**Alternative brownfield track — OpenSpec.**
[Lab 04](lab-04-brownfield-soft-delete-with-openspec.md) (~60 min) delivers the
*same* soft-delete request with **OpenSpec** (propose → apply → archive) and
compares it with the Spec Kit route of Labs 02–03. Do it instead of Labs 02–03,
or afterwards from the pre-implementation commit. Needs Node.js 20.19+ and
`npm install -g @fission-ai/openspec@latest`.

## The two pieces of work

### Greenfield (Lab 01) — finish the SDLC for **task comments**

The comments feature from Module 04 is *implemented and validated* but not
*shipped*: it has no integration tests, no CI quality gate, and no
release-readiness sign-off. Lab 01 completes those stages.

### Brownfield (Labs 02–03) — **soft-delete for tasks**

A change to **existing behaviour**, described informally in
[feature-request.md](feature-request.md):

> `DELETE /api/tasks/{id}` currently removes the row for good. Change it to a
> **soft delete** — the task is marked deleted and disappears from the board and
> the API by default, but can be restored. Add a way to list deleted tasks and
> to purge one permanently.

This deliberately touches code that already works — every list query, every
"the task is gone" test, the comment cascade, the stats endpoint, the frontend.
That blast radius is the whole point.

## Prerequisites

- **Modules 01–04 completed.** Task Board runs locally; the comments feature
  (`specs/001-task-comments/`) is on your branch; the `.github/` layer
  (instructions, prompts, chat modes, skills, `ci.yml`, `copilot-setup-steps.yml`)
  and `CONTEXT.md` are present.
- [Module 01 prerequisites](../setup/prerequisites.md) + a working backend,
  frontend, and database.
- **`specify` CLI** installed (Module 04 set-up). `specify --version`.
- **GitHub Copilot** in VS Code; the repo pushed to GitHub (Module 02 Lab 06)
  so CI runs.
- **Docker** available for integration tests (the labs use a real Postgres
  container).

## Platform conventions

Shell blocks are given for **macOS / Linux (bash/zsh)** and **Windows
(PowerShell)**. WSL2 users follow the macOS / Linux side. Copilot Chat and Spec
Kit slash-commands are identical on every OS.

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

### 2. Branch from your Module 04 work

```bash
git checkout 001-task-comments        # or wherever the comments feature landed
git checkout -b module-05-sdlc
```

### 3. Confirm the starting state

**macOS / Linux**

```bash
ls specs/001-task-comments/spec.md .github/workflows/ci.yml CONTEXT.md
cd backend-python && pytest -q ; cd ../frontend && npm test -- --run ; cd ..
```

**Windows (PowerShell)**

```powershell
Get-ChildItem specs\001-task-comments\spec.md, .github\workflows\ci.yml, CONTEXT.md
cd backend-python ; pytest -q ; cd ..\frontend ; npm test -- --run ; cd ..
```

Everything green + those files present → you're ready.
[Start Lab 01](lab-01-greenfield-spec-to-release.md).

## How each lab is structured

Objective → Why it matters for the enterprise → Background → Steps (both
platforms) → Files/templates → Verify → Troubleshooting → Recap & carry-forward.

## After this module

- The comments feature is release-ready with a CI quality gate.
- The repo carries a reusable archaeology + change-impact method for brownfield
  work.
- **Module 06** derives its test strategy directly from what you build here and
  proves it catches a deliberately injected defect.
