# Module 06 — Test Strategy, Testcontainers & End-to-End Validation (Hands-On Lab)

## What this lab is

Module 05 shipped two features — **task comments** (greenfield) and **soft-delete
for tasks** (brownfield). Module 06 proves them: it derives a **test strategy**
from the specification, builds a **test pyramid** with real dependencies via
**Testcontainers**, and then breaks the feature on purpose to prove the strategy
catches it. Same Task Board codebase, same `specs/` and `.github/` layer from
Modules 02–05. No new app.

| Lab | Focus | You produce |
|-----|-------|-------------|
| [01](lab-01-derive-the-test-strategy.md) | Spec → test strategy, traceability, test data | `test-strategy.md` (criterion → test-type map + test data + gaps) |
| [02](lab-02-testcontainers-integration-and-contract.md) | Trustworthy integration & contract tests | Testcontainers-backed suite, contract tests, CI wiring |
| [03](lab-03-e2e-and-defect-injection.md) | End-to-end flow + prove it works | E2E test, `defect-injection-report.md` |

Work through them in order. Total time: about **2 hours**.

## The feature under test

The **soft-delete for tasks** feature from Module 05 (`specs/002-task-soft-delete/`)
is the primary subject — it is brownfield, touches many read paths, and has a
rich set of failure modes. The **comments** feature is the secondary subject for
the contract and E2E work.

## Prerequisites

- **Modules 01–05 completed.** Task Board runs locally; `specs/001-task-comments/`
  and `specs/002-task-soft-delete/` are on your branch with their
  `spec.md` / `acceptance-checklist.md`; the `.github/` layer and `ci.yml` are
  present.
- [Module 01 prerequisites](../setup/prerequisites.md) + a working backend and
  frontend.
- **Docker** running — Testcontainers needs it. Check `docker info`.
- **GitHub Copilot** in VS Code; the repo pushed to GitHub so CI runs.

## Platform conventions

Shell blocks are given for **macOS / Linux (bash/zsh)** and **Windows
(PowerShell)**. WSL2 users follow the macOS / Linux side.

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

### 2. Branch from your Module 05 work

```bash
git checkout module-05-sdlc        # or wherever Module 05 landed
git checkout -b module-06-testing
```

### 3. Confirm the starting state

**macOS / Linux**

```bash
docker info > /dev/null && echo "docker ok"
ls specs/002-task-soft-delete/spec.md specs/001-task-comments/spec.md .github/workflows/ci.yml
cd backend-python && pytest -q ; cd ../frontend && npm test -- --run ; cd ..
```

**Windows (PowerShell)**

```powershell
docker info | Out-Null ; "docker ok"
Get-ChildItem specs\002-task-soft-delete\spec.md, specs\001-task-comments\spec.md, .github\workflows\ci.yml
cd backend-python ; pytest -q ; cd ..\frontend ; npm test -- --run ; cd ..
```

Green + Docker up → [start Lab 01](lab-01-derive-the-test-strategy.md).

## How each lab is structured

Objective → Why it matters for the enterprise → Background → Steps (both
platforms) → Files/templates → Verify → Troubleshooting → Recap & carry-forward.

## After this module

- Both features carry a spec-derived, traceable test suite proven against a real
  defect.
- **Module 07** connects the agents doing this work to approved tools under
  governance and packages the patterns as reusable skills.
