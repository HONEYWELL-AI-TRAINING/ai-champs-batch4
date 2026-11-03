# Module 09 — Studio-Style Workflows with Atlassian Rovo Studio (Hands-On Lab)

## What this lab is

Modules 02–08 built and governed the *engineering* work — Copilot, MCP, specs,
tests, PR gates. Module 09 is the layer **above** that: how a non-code or
semi-technical user (Product Owner, TPO, RTE, Scrum roles) shapes agent
behaviour in **Atlassian Rovo Studio** to *coordinate* that engineering work —
program reporting, issue triage, release coordination — then hands the finished
workflow to a technical owner **without bypassing governance**.

No new app. The workflow you build coordinates the **soft-delete feature**
(`specs/002-task-soft-delete/`) that Modules 05–08 shipped: it reads the Jira
epic and Confluence release page, drafts a release digest and a program-status
summary, and routes them through a human approval checkpoint before anything is
published.

| Lab | Focus | You produce |
|-----|-------|-------------|
| [01](lab-01-ground-and-build-the-workflow.md) | Grounding, triggers, actions, approval checkpoints | `workflows/release-digest/workflow-spec.md`, `test-log.md` |
| [02](lab-02-govern-and-hand-over.md) | Permissions, versioning, ownership, the governance boundary | `governance-review.md`, `handoff-note.md`, a published v1.0 workflow |

Work through them in order. Total time: about **1 hour**.

## Where a studio workflow sits

```
Business intent  ──▶  Studio workflow (Rovo Studio)  ──▶  ⟪governance boundary⟫  ──▶  Engineering agent (Copilot / MCP, Modules 02–08)
 program report        reads project data, applies         business author →           opens PRs, runs tests,
 · triage · release     rules, routes, drafts               technical owner            merges under the M08 gate
```

A studio workflow **coordinates** engineering work. It reads Jira/Confluence,
applies rules, drafts and routes — it does **not** write code, merge a PR, or
transition an issue without a person confirming. That boundary is the whole point
of the module.

## Prerequisites

- **Modules 01–08 completed.** `specs/002-task-soft-delete/` carries the spec,
  plan, test strategy, and the Module 08 PR artifacts on your branch.
- [Module 01 prerequisites](../setup/prerequisites.md) + `git` on PATH (only used
  to commit the markdown artifacts).
- **Atlassian Rovo** enabled on your Atlassian Cloud site, with **Rovo Studio**
  access ([what is Rovo Studio](https://support.atlassian.com/rovo/docs/what-is-rovo-studio/)).
  A Jira project and a Confluence space you can use for testing.
  - **No Rovo Studio access?** The lab still works: you author the same workflow
    **as a specification** in `workflow-spec.md` and dry-run it on paper against
    the sample data. Every artifact and every governance decision is identical.
    Steps that require the Studio UI are marked **[Studio]**; do the **[Spec]**
    equivalent instead.
- A sample **Jira epic** for the soft-delete feature (create one: epic
  "Task soft-delete", 3–4 child stories mirroring `specs/002`), and a
  **Confluence page** "Task Board — Release Notes" in your test space.

## Platform conventions

Rovo Studio is a web application — the UI is identical on every OS. The only
shell commands are `git` for committing artifacts; they are shown once where they
don't differ by platform.

## Set-up — do this once before Lab 01

### 1. Branch from your Module 08 work

```bash
cd labs/module-01
git checkout module-08-pr-automation      # or wherever Module 08 landed
git checkout -b module-09-studio
mkdir -p workflows/release-digest
```

On Windows PowerShell the `mkdir` is the same; use `cd labs\module-01`.

### 2. Copy the templates

**macOS / Linux**

```bash
cp ../module-09/templates/workflow-spec-template.md   workflows/release-digest/workflow-spec.md
cp ../module-09/templates/governance-review-template.md workflows/release-digest/governance-review.md
cp ../module-09/templates/handoff-note-template.md     workflows/release-digest/handoff-note.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-09\templates\workflow-spec-template.md    workflows\release-digest\workflow-spec.md
Copy-Item ..\module-09\templates\governance-review-template.md workflows\release-digest\governance-review.md
Copy-Item ..\module-09\templates\handoff-note-template.md      workflows\release-digest\handoff-note.md
```

### 3. Prepare the sample data

In your Atlassian test site:
- **Jira:** an epic **"Task soft-delete"** with child stories for
  `deleted_at` column, default-exclude filter, `/restore` endpoint, and
  `?permanent=true`. Set a couple to *Done*, leave one *In Progress*.
- **Confluence:** a page **"Task Board — Release Notes"** with an empty
  "Unreleased" section.

Then → [start Lab 01](lab-01-ground-and-build-the-workflow.md).

## How each lab is structured

Objective → Why it matters for the enterprise → Background → Steps (**[Studio]** /
**[Spec]** where they differ) → Files/templates → Verify → Troubleshooting →
Recap & carry-forward.

## After this module

- A studio workflow exists that turns "the soft-delete epic is ready" into a
  drafted release digest and program report — with a human approval gate.
- Its permission, versioning, and ownership implications are documented, and it
  has been handed to a named technical owner.
- **Module 10** points Agent Prism at this workflow and the engineering agents
  alike — same traces, same cost view. Module 11 folds its run cost into the ROI
  model.
