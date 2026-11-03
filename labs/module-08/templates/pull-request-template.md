<!--
Copy to .github/pull_request_template.md (repo root of labs/module-01).
This is the evidence a PR must carry before the quality gate and the judge run.
-->

## What & why

- Spec / issue: <link to `specs/<feature>/spec.md` or the issue>
- Summary (1–3 sentences):
- Greenfield or brownfield:

## Spec conformance

- [ ] Every acceptance criterion in the spec is implemented
- [ ] `spec-validator` run — report: <link to `spec-validation-report.md`>
- [ ] `usecase.md` API contract updated (if the contract changed)
- [ ] No behaviour shipped that isn't in the spec

## Test evidence

- [ ] Unit tests added/updated — `<command>` → <result>
- [ ] Integration tests (Testcontainers) — <result>
- [ ] Contract tests — <result>
- [ ] Changed-file coverage: <%>
- Traceability: <link to `traceability.md` / `test-strategy.md` §2>

## Change safety (brownfield only)

- [ ] Change-impact analysis: <link to `change-impact.md`>
- [ ] Full pre-existing suite green before **and** after — <link to `regression-report.md`>
- [ ] Every intentionally-changed test is justified in that report
- [ ] Change stayed within the documented blast radius

## Security & ops

- [ ] No secrets in the diff
- [ ] Dependencies: no new high-severity advisories
- [ ] Rollback plan:

## Reviewer notes

- Riskiest part of this change:
- Anything you want a human to look at specifically:
