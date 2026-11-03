# Governance Review — <workflow name>

Copy to `workflows/<slug>/governance-review.md`. Completed by the business author
with a technical owner before publishing. Mirrors the Module 07
`mcp-governance-checklist.md` structure so the two reviews line up.

## 1. Identity & permission-aware access

| Question | Answer |
|----------|--------|
| What identity does the workflow run as? | <the invoking user · a scoped service account — name it> |
| What Jira projects can that identity see? | |
| What Confluence spaces can that identity see / write? | |
| Can it see more than the business author personally can? | should be **no** — explain if yes |
| What happens if grounding access is denied at run time? | must fail safe, no partial action |

## 2. Data boundary

| Data | Direction | Boundary |
|------|-----------|----------|
| Jira epic + stories | in (read) | grounded scope only |
| Confluence release page | in (read) / out (draft) | one named page/space |
| Repo specs | in (read-only) | `specs/002-*` only, via the Module 07 governed connection |
| Program channel | out (post) | after approval only |
| Anything **not** listed | — | not permitted |

Does any output contain data a recipient shouldn't see (e.g. internal Jira notes
in an external summary)? → mitigation:

## 3. Approval & human-in-the-loop

| Question | Answer |
|----------|--------|
| Which steps are gated by a human? | |
| Can any sensitive action run without approval? | should be **no** |
| Is the approver distinct from the author? | |
| Is the approval recorded (who, when, on what version)? | |

## 4. Versioning

| Question | Answer |
|----------|--------|
| Published version | v1.0.0 |
| Where is the version visible to consumers? | |
| How is a change reviewed before it ships? | |
| How do you roll back? | |
| Change log location | `workflows/<slug>/CHANGELOG.md` |

## 5. Ownership

| Role | Name | Accountable for |
|------|------|-----------------|
| Business owner | | workflow intent, output quality, stakeholder fit |
| Technical owner | | runtime, connectors, permissions, incident response |
| Approver(s) | | sign-off on each run |

## 6. Governance boundary (handoff)

| Question | Answer |
|----------|--------|
| What does the business author hand over, and to whom? | |
| What can the technical owner change without re-consulting the author? | |
| What must come back to the author for a decision? | |
| Where does engineering execution take over? | the Module 08 PR gate — this workflow never crosses it |

## 7. Sign-off

- [ ] Business owner: the workflow does what the scenario needs — <name / date>
- [ ] Technical owner: identity, data boundary, and approval gates are acceptable
      for a governed runtime — <name / date>
- [ ] Both: the non-goals in `workflow-spec.md` §8 are complete and enforced
