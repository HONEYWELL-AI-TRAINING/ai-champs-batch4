# Lab 03 — Run the Flow Against a Flawed Change, and Measure It

**Time:** ~30 min · **Surface:** git + GitHub.com + Copilot Chat ·
**Prereq:** Labs 01–02 complete (quality gate + judge, calibrated)

## Objective

Create a deliberately flawed PR, run the full review flow — quality gate →
Copilot review → LLM-as-Judge → human escalation — capture the evidence at each
stage, then run a clean PR through the same flow and compare. Measure the
review-cycle reduction.

## Why it matters for the enterprise

A review pipeline is only trustworthy once you've watched it catch something real
and *not* over-block something clean. This lab produces that evidence, and the
review-cycle numbers feed Module 11's ROI model directly.

## Step 1 — Build the flawed change

```bash
git checkout -b m08-flawed-pr
```

(Same command on every OS.)

Make a change to the soft-delete feature that contains **three planted flaws**.
Write them down in `specs/002-task-soft-delete/flawed-change.md` first (so the
lab is reproducible), then implement:

| # | Flaw | Type | Should be caught by |
|---|------|------|---------------------|
| 1 | Add a new `GET /api/tasks/deleted-count` endpoint whose query runs **in the router**, not the repository | constitution / spec | Copilot review (J2) + `spec-validator` (no such AC) |
| 2 | The new endpoint has **no test** | test evidence | quality gate (coverage) + judge (J4 = 0) |
| 3 | It logs the full DB connection string on error (`logger.error(f"failed: {settings.database_url}")`) | security | secret-scan awareness + judge (J3 = 0) |

Commit and push:

```bash
git commit -am "Add deleted-count endpoint (planted flaws for M08 Lab 03)"
git push -u origin m08-flawed-pr
gh pr create --fill    # fill the template — note the flaws honestly? No: fill it as an unaware author would
```

> Fill the PR template as a **real author who didn't notice the flaws** would —
> that's the realistic test of the gate.

## Step 2 — Run the flow, capture each stage

**macOS / Linux**

```bash
cp ../module-08/templates/pr-automation-report-template.md specs/002-task-soft-delete/pr-automation-report.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-08\templates\pr-automation-report-template.md specs\002-task-soft-delete\pr-automation-report.md
```

1. **Quality gate:** `gh pr checks --watch`. Record which checks failed (expect:
   coverage, maybe secret-scan).
2. **Copilot review:** request it (`gh pr edit --add-reviewer "@copilot"` if not
   automatic). Record the comments — did it name flaw 1 (router-layer query)
   with a `file:line` + the constitution rule?
3. **Spec-validator skill** (Module 07): run it on the branch. Does it flag flaw
   1 as unspecified behaviour?
4. **LLM-as-Judge:** run `/pr-judge` with the diff, the spec, and the review
   comments pasted. Record J1–J6, overall, confidence, and the decision.
5. **Escalation:** the judge should **escalate** (J3 and J4 at 0). Act as the
   human reviewer: request changes on the PR, citing the judge's evidence.

## Step 3 — Run a clean PR through the same flow

Use a real, correct small change (or the Lab 01 smoke-test PR). Run gate →
review → judge. The judge should **fast-track** it (PASS, HIGH/MEDIUM
confidence). Record it in the report's "Clean PR" column.

## Step 4 — Measure review-cycle reduction

Fill the report's measurement table. Estimate the **manual baseline**: how long
would a human reviewer take to find those three flaws unaided, and how many
review round-trips (comment → fix → re-review)? Compare to: the gate + judge
surfaced them in one automated pass, with evidence, before a human spent a
minute.

Key numbers for Module 11:
- Issues found before a human looked: **3 vs 0**
- Human review time: automated-triaged vs cold-read
- Round trips to merge-ready

## Step 5 — Close the loop and clean up

- Flawed PR: after "human requests changes", **close it** (it was a test) — or
  fix all three flaws properly and let it pass.
- `git checkout module-08-pr-automation && git branch -D m08-flawed-pr`
- Move `flawed-change.md` and `pr-automation-report.md` onto
  `module-08-pr-automation`.

```bash
git add specs/002-task-soft-delete/flawed-change.md specs/002-task-soft-delete/pr-automation-report.md
git commit -m "Module 08 Lab 03: flawed-vs-clean PR flow + review-cycle measurement"
git push
```

## Verify

- [ ] `flawed-change.md` documents the three planted flaws and their expected
      catch points.
- [ ] Each flaw was caught by **some** stage, with the stage recorded in
      `pr-automation-report.md`.
- [ ] The judge **escalated** the flawed PR and **fast-tracked** the clean one.
- [ ] The measurement table has a manual baseline and the automated comparison.
- [ ] A human acted on the escalation (requested changes citing evidence), then
      the flawed PR was closed or fixed.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| A flaw slips through every stage | That's the finding — which check/rubric criterion has the hole? Fix it (a gate check, or a rubric anchor), re-run, record. |
| Copilot review misses the layer violation | Confirm `code-review.instructions.md` (with the constitution rules) is on the PR base branch. |
| Judge escalates the clean PR too | Re-calibrate (Lab 02 Step 3) — the rubric is too strict on a MEDIUM-confidence pass. |
| Secret-scan doesn't catch flaw 3 | A logged variable isn't a committed secret — the *judge* (J3) is the backstop here; make sure it flags "logs sensitive config". |

## Recap — Module 08 & the Build & Validate phase complete

The repo now carries:

```
.github/
├── pull_request_template.md        # Lab 01 — evidence required
├── pr-judge-rubric.md              # Lab 02 — J1–J6, confidence, escalation, calibration
├── prompts/pr-judge.prompt.md      # Lab 02 — /pr-judge
├── instructions/code-review.instructions.md  # Lab 01 — evidence-based comments
└── workflows/ci.yml                # Lab 01 — quality-gate job
specs/002-task-soft-delete/
├── quality-gate.md                 # Lab 01
├── flawed-change.md                # Lab 03
└── pr-automation-report.md         # Lab 03 — caught the flaws, measured the saving
```

Across Modules 05–08 you carried one spec through a full SDLC, evolved existing
code safely, proved it with a defect-tested strategy, governed the agents with
MCP and reusable skills, and gated the PR with AI review + an LLM-as-Judge. The
**Scale & Govern** phase (Modules 09–11) takes this to studio workflows for
non-technical roles, Agent Prism observability, and the ROI model your cost logs
have been feeding — closing with the Module 12 capstone.
