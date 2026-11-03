# Lab 02 — LLM-as-Judge: Rubric, Confidence & Escalation

**Time:** ~30 min · **Surface:** file editing + Copilot Chat ·
**Prereq:** Lab 01 complete (quality gate + evidence-based review)

## Objective

Build the judgement layer: a rubric that scores a PR (and the AI review of it)
across six criteria, a prompt file that produces a structured verdict with a
**confidence** level, and an explicit **escalate-to-human** rule. Calibrate it
against PRs you already know the answer for.

## Why it matters for the enterprise

Automated review can be confidently wrong. LLM-as-Judge adds a second, rubric-
bound pass that also reports *how sure it is* — and hands the hard cases to a
human instead of rubber-stamping them. The measured outcome is **review-cycle
reduction**: faster reviews without losing the human call on the cases that need
it.

## Background

```
PR + evidence ──▶ Quality gate (Lab 01) ──▶ Copilot review (Lab 01) ──▶ LLM-as-Judge (this lab)
                                                                          │
                                              score J1–J6 + confidence ───┤
                                                                          ▼
                                        PASS + HIGH confidence ──▶ fast-track (light human approval)
                                        any 0 / security / LOW  ──▶ escalate to human
```

---

## Step 1 — The rubric

**macOS / Linux**

```bash
cp ../module-08/templates/llm-judge-rubric-template.md .github/pr-judge-rubric.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-08\templates\llm-judge-rubric-template.md .github\pr-judge-rubric.md
```

Adjust the criteria to this repo: J2 should name the constitution principles
(layering, 404/422/409, schema ownership); J5's "pre-existing suite" is the
Module 06 test suite. Keep the escalation rules strict — the point is to catch,
not to pass.

## Step 2 — The judge prompt file

```md
<!-- .github/prompts/pr-judge.prompt.md -->
---
description: LLM-as-Judge — score a PR against .github/pr-judge-rubric.md with confidence and an escalation decision
mode: ask
---
You are an impartial reviewer of a pull request AND of the AI review already
posted on it. You do not edit code.

Inputs:
- The diff: ${input:diff_ref:branch or PR number}
- Its spec: ${input:spec_path:e.g. specs/002-task-soft-delete/spec.md}
- The AI review comments already on the PR (I will paste them, or you read them)
- `.github/pr-judge-rubric.md`
- `.specify/memory/constitution.md`

Do:
1. Score J1–J6 per the rubric. For each score, cite the evidence (file:line,
   acceptance-criterion id, or "no evidence found").
2. Judge the AI review itself: did it catch the real issues, or miss/over-flag?
3. Set confidence HIGH/MEDIUM/LOW and say why (how much context you had, diff
   size, tests runnable).
4. Apply the verdict and escalation rules from the rubric exactly.
5. Emit the rubric's output format. Nothing else.

Be strict. A PASS you're not sure about is a LOW-confidence escalation, not a PASS.
```

## Step 3 — Calibrate against known cases

Pick PRs whose outcome you already know:

| Case | Source | Expected judge output |
|------|--------|----------------------|
| **Known good** | the clean smoke-test PR from Lab 01, or a merged feature PR | PASS, HIGH/MEDIUM confidence, fast-track |
| **Known bad — spec** | Module 06's defect-injection branch (a `deleted_at` filter removed) | J1/J4 = 0, FAIL, escalate |
| **Known bad — vague** | any PR with a real change but no test | J4 = 0, escalate |

Run `/pr-judge` for each. If the judge passes a known-bad case or escalates a
clean one, fix the rubric (anchor the levels harder) or the prompt (more
explicit evidence requirement), and re-run. Record the calibration in a
`## Calibration` section of `pr-judge-rubric.md`.

## Step 4 — Wire it into the flow (lightweight)

You can run `/pr-judge` by hand on any PR. To make it routine, add a note to the
PR template:

```md
<!-- append to .github/pull_request_template.md -->

## Judge
- [ ] `/pr-judge` run — paste the verdict block here, or link it:
```

(A full CI integration — posting the judge verdict as a PR comment via a workflow
that calls a model API — is a Module 09/10 topic. For now the human running
`/pr-judge` before merge is the loop.)

## Step 5 — Commit

```bash
git add .github/pr-judge-rubric.md .github/prompts/pr-judge.prompt.md .github/pull_request_template.md
git commit -m "Module 08 Lab 02: LLM-as-Judge rubric + prompt + calibration"
git push
```

## Verify

- [ ] `.github/pr-judge-rubric.md` has anchored 0/1/2 descriptions for J1–J6,
      verdict rules, and strict escalation rules.
- [ ] `/pr-judge` produces the rubric's exact output format with per-criterion
      evidence and a confidence level.
- [ ] Calibration: known-good → fast-track; known-bad → escalate. Recorded.
- [ ] The judge escalates (not passes) when it's unsure.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Judge always says HIGH confidence | Add to the prompt: "LOW if you couldn't run the tests, the diff is > 400 lines, or the spec is missing." |
| Judge passes a known-bad PR | The rubric level for "0" is too soft. Make it concrete: "0 = an acceptance criterion has no test OR is implemented incorrectly." |
| Verdict format drifts | Paste the output template into the prompt; say "emit exactly this, nothing before or after". |
| Judge and Copilot review always agree | Feed the judge the review comments explicitly and ask it to critique them — that's half its job. |

## Recap & carry-forward

You have a rubric-bound judge with confidence and escalation. **Lab 03** runs the
whole flow — gate → review → judge → human — against a deliberately flawed PR,
proves the flaws are caught, and measures the review-cycle reduction.
