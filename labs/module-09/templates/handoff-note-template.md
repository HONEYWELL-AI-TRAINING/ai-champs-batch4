# Handoff Note — <workflow name>

Copy to `workflows/<slug>/handoff-note.md`. One page. The business author gives
this, plus `workflow-spec.md` and `governance-review.md`, to the technical owner.

## What this is

<One paragraph: the scenario, who asked for it, what it produces, and that it has
been tested against sample data.>

## Current state

| | |
|--|--|
| Rovo Studio location | <link, or "spec only — not yet built in Studio"> |
| Version | v1.0.0 |
| Tested against | <sample Jira epic + Confluence page> — see `workflow-spec.md` §9 |
| Test result | <pass / pass-with-notes> |
| Known limitations | |

## What I need from the technical owner

- [ ] Review identity & permissions in `governance-review.md` §1 and confirm the
      runtime identity (scoped service account vs invoking user).
- [ ] Confirm the connected sources (Jira, Confluence, the `specs/` read
      connection) match the Module 07 governed connection policy.
- [ ] Confirm the approval checkpoint cannot be skipped in the target runtime.
- [ ] Take ownership of connectors and incident response; add yourself to
      `governance-review.md` §5.
- [ ] Wire Module 10 (Agent Prism) tracing before promoting beyond the pilot.

## What stays with me (business owner)

- The workflow's intent and the wording of the digest / program summary.
- Deciding when a scenario change needs a new version.
- Being the named approver, or nominating one.

## Explicitly out of scope for this workflow

It does not touch code, PRs, or the Module 08 merge gate. If a stakeholder asks
for "and then it merges the release branch", that is a **separate** engineering
agent request — route it to the engineering team, don't extend this workflow
across the governance boundary.

## Links

- Spec: `workflows/<slug>/workflow-spec.md`
- Governance review: `workflows/<slug>/governance-review.md`
- Feature specs: `specs/002-task-soft-delete/`
- Module 07 governance checklist: `specs/002-task-soft-delete/mcp-governance.md`
