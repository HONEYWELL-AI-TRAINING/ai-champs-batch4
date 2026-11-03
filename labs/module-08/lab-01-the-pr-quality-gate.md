# Lab 01 — The PR Quality Gate

**Time:** ~30 min · **Surface:** file editing + CI + GitHub.com ·
**Prereq:** Module 08 [set-up](README.md#set-up--do-this-once-before-lab-01) done

## Objective

Build the mechanical half of the review gate: a PR template that requires
evidence, a `quality-gate` CI job that checks spec compliance signals, standards,
security, test evidence, and regression risk, and Copilot code review tuned to
leave **evidence-based** comments.

## Why it matters for the enterprise

Most review time is spent on things a machine can check: is there a test? does it
lint? is the coverage there? is the spec linked? Automating those frees the human
reviewer for the judgement calls — architecture fit, subtle correctness, risk. A
quality gate makes review coverage **consistent** instead of dependent on who
picked up the PR.

## Background — what the gate checks

| Dimension | Mechanical check |
|-----------|------------------|
| Spec compliance | PR links a spec; `spec-validator` report attached; contract doc updated |
| Coding / design standards | lint clean; constitution rules (via `copilot-instructions.md` in review) |
| Security | no secrets in diff; dependency advisory scan |
| Test evidence | tests present and passing; changed-file coverage ≥ bar |
| Regression risk | full pre-existing suite green; (brownfield) regression report linked |

---

## Step 1 — PR template

**macOS / Linux**

```bash
cp ../module-08/templates/pull-request-template.md .github/pull_request_template.md
```

**Windows (PowerShell)**

```powershell
Copy-Item ..\module-08\templates\pull-request-template.md .github\pull_request_template.md
```

Review it — trim anything that doesn't apply to this repo, keep the evidence
sections. From now, every `gh pr create` starts from this.

## Step 2 — The `quality-gate` CI job

Ask Copilot (Agent mode) to add it to `.github/workflows/ci.yml`:

```
Add a job "quality-gate" to .github/workflows/ci.yml that runs on pull_request
and:
1. Fails if the PR body has no link to a specs/*/spec.md or an issue (parse
   ${{ github.event.pull_request.body }}).
2. Runs ruff (Python) and the frontend's oxlint — fail on any error.
3. Secret scan: fail if the diff adds anything matching common secret patterns
   (gitleaks action, or a grep for token/key/password assignments).
4. Dependency check: fail on a new HIGH/CRITICAL advisory (pip-audit for
   backend-python; npm audit --audit-level=high for frontend).
5. Changed-file coverage: run pytest --cov, use diff-cover against the base
   branch, fail below 80%.
6. Depends on the existing test jobs passing (needs:).
Keep actions/* pinned to major versions. Show me the job.
```

Reconcile with the `ci.yml` you already have from Modules 02/05/06 — extend,
don't replace.

## Step 3 — Tune Copilot review for evidence-based comments

Update `.github/instructions/code-review.instructions.md` (from Module 02, Lab 07):

```md
<!-- append to .github/instructions/code-review.instructions.md -->

## Comment style — evidence-based only
Every comment MUST have:
- the exact `file:line`
- the rule it breaks (a constitution principle, an acceptance criterion id, a
  contract row in usecase.md) — quoted
- the smallest concrete fix

Do NOT post: "consider refactoring", "add error handling", "this could be
cleaner", or any comment without a file:line and a named rule. If the change is
clean, say so and stop.

## Priorities (highest first)
1. Spec compliance — a change that doesn't match its spec.md acceptance criteria
2. Constitution violations — layering, 404/422 (+409) error contract, schema ownership
3. Missing test for changed behaviour
4. Security — secrets, unsafe input handling
5. Regression risk — a pre-existing test changed without justification
```

## Step 4 — Prove the gate

Open a small **real** PR (e.g. a doc fix or a tiny refactor) with the template
filled in:

```bash
git checkout -b m08-gate-smoketest
# make a trivial, correct change
git commit -am "docs: clarify soft-delete restore behaviour in usecase.md"
git push -u origin m08-gate-smoketest
gh pr create --fill
gh pr checks --watch
```

Confirm: the `quality-gate` job runs; lint/secret/dependency/coverage checks
report; Copilot review posts comments that all have a `file:line` + a named rule
(or says it's clean). Then either merge it or close it — it was a smoke test.

## Step 5 — Write `quality-gate.md`

Document the gate: each check, what makes it pass, and what a failure means for
the author. Save to `specs/002-task-soft-delete/quality-gate.md` (it's
repo-wide, but living it next to the feature is fine for the course).

## Step 6 — Commit

```bash
git checkout module-08-pr-automation
git add .github/pull_request_template.md .github/workflows/ci.yml .github/instructions/code-review.instructions.md specs/002-task-soft-delete/quality-gate.md
git commit -m "Module 08 Lab 01: PR template + quality-gate CI job + evidence-based review"
git push
```

## Verify

- [ ] `.github/pull_request_template.md` prefills new PRs with the evidence
      sections.
- [ ] `ci.yml` has a `quality-gate` job covering spec link, lint, secrets,
      dependencies, and changed-file coverage.
- [ ] The smoke-test PR ran the gate and got only evidence-based review comments
      (or a clean pass).
- [ ] `quality-gate.md` documents each check and its pass criteria.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Coverage check fails on every PR | Gate on changed files (`diff-cover`), not whole-project; exclude generated/`dist` paths. |
| Secret scan false-positives on test fixtures | Add an allowlist for `tests/` fixture values, or use gitleaks' `.gitleaksignore`. |
| Copilot review still vague | The instruction file must be on the PR **base** branch. Make the "no comment without file:line + rule" line firm. |
| PR-body parsing brittle | Accept any of: a `specs/…/spec.md` path, a `#123` issue ref, or a `Closes #123`. |

## Recap & carry-forward

The mechanical gate is in place. **Lab 02** adds the judgement layer — an
LLM-as-Judge that scores the PR against a rubric, reports confidence, and decides
whether a human needs to look.
