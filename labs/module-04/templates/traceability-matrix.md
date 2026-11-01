# Traceability Matrix — Task Comments

Copy to `specs/001-task-comments/traceability.md`. Start it in Lab 02 (REQ →
TASK), extend it in Lab 03 (→ commit/PR → test), and close it in Lab 04 after
the change-control exercise.

## Requirements → Tasks → Implementation → Acceptance

| REQ | Requirement (from spec.md) | Task(s) | Commit / PR | Acceptance test(s) | Status |
|-----|----------------------------|---------|-------------|--------------------|--------|
| REQ-01 | | | | | ☐ |
| REQ-02 | | | | | ☐ |
| REQ-03 | | | | | ☐ |
| REQ-04 | | | | | ☐ |
| REQ-05 | | | | | ☐ |
| … | | | | | ☐ |

## Rules

- **No orphan code.** Every task and every commit maps back to a REQ. If you
  wrote code that maps to no requirement, either add the requirement to the spec
  (change control) or remove the code.
- **No orphan requirements.** Every REQ has at least one task and one acceptance
  test. A REQ with no test is not testable — fix the spec.
- **Change control:** when a requirement changes, add a row (or a `REQ-0x-v2`)
  and record which artifacts were regenerated. Never edit code for a spec change
  without the spec changing first.

## Change log (Lab 04)

| Date | What changed in the spec | Artifacts regenerated | New/changed tasks | New/changed tests |
|------|--------------------------|-----------------------|-------------------|-------------------|
| | | | | |
