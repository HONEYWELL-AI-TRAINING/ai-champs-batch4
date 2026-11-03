# Module 08 — PR Process Automation, Quality Gates & LLM-as-Judge (Hands-On Lab)

## What this lab is

Modules 04–07 produced a validated, governed feature with test and workflow
evidence. Module 08 is the **review gate**: a pull request that carries automated
quality-gate evidence, is checked by AI review **and** an LLM-as-Judge against an
explicit rubric, and escalates to a human only when confidence is low or the
rubric fails. Same Task Board codebase and `.github/` layer. No new app.

| Lab | Focus | You produce |
|-----|-------|-------------|
| [01](lab-01-the-pr-quality-gate.md) | The mechanical quality gate | `.github/pull_request_template.md`, a `quality-gate` CI job, `quality-gate.md` |
| [02](lab-02-llm-as-judge-rubric.md) | LLM-as-Judge with confidence + escalation | `.github/prompts/pr-judge.prompt.md`, `pr-judge-rubric.md` |
| [03](lab-03-run-against-a-flawed-change.md) | Run the whole flow, measure review-cycle reduction | `flawed-change.md`, `pr-automation-report.md` |

Work through them in order. Total time: about **1.5 hours**.

## Prerequisites

- **Modules 01–07 completed.** Task Board runs; `specs/001-…` and `specs/002-…`
  carry specs, test strategies, and (Module 07) `spec-validator` +
  `spec-validation-report.md`; `.github/copilot-instructions.md`,
  `code-review.instructions.md`, `ci.yml` are present; the repo is on GitHub with
  Copilot code review enabled (Module 02, Lab 07).
- [Module 01 prerequisites](../setup/prerequisites.md) + `gh` CLI authenticated.
- **GitHub Copilot** in VS Code; a strong reasoning model available in your model
  picker (for the judge).

## Platform conventions

Shell blocks are given for **macOS / Linux (bash/zsh)** and **Windows
(PowerShell)**. `git` and `gh` are cross-platform; commands are shown once where
they don't differ.

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

### 2. Branch from your Module 07 work

```bash
git checkout module-07-mcp        # or wherever Module 07 landed
git checkout -b module-08-pr-automation
```

### 3. Confirm the starting state

**macOS / Linux**

```bash
ls .github/copilot-instructions.md .github/instructions/code-review.instructions.md .github/workflows/ci.yml
ls .github/skills/spec-validator/SKILL.md
gh auth status
```

**Windows (PowerShell)**

```powershell
Get-ChildItem .github\copilot-instructions.md, .github\instructions\code-review.instructions.md, .github\workflows\ci.yml, .github\skills\spec-validator\SKILL.md
gh auth status
```

Present → [start Lab 01](lab-01-the-pr-quality-gate.md).

## How each lab is structured

Objective → Why it matters for the enterprise → Background → Steps (both
platforms) → Files/templates → Verify → Troubleshooting → Recap & carry-forward.

## After this module

- Every PR on this repo carries evidence, an AI review, a judged verdict, and a
  clear human-escalation rule.
- This completes the **Build & Validate** phase. The Scale & Govern phase
  (Modules 09–11) adds studio workflows for non-technical roles, Agent Prism
  observability, and the ROI / token-economics model that every lab's cost logs
  have been feeding.
