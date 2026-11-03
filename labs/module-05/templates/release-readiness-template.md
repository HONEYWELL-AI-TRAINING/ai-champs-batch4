# Release-Readiness Report — <feature name>

Copy to `specs/<nnn>-<slug>/release-readiness.md`. Complete it before marking a
feature shippable (Lab 01 for greenfield; Lab 03 for the brownfield change).
Every "yes" needs evidence — a link, a file, a CI run, a command output.

## Spec conformance

| Check | Evidence | ✅ |
|-------|----------|:--:|
| Every `REQ` in `spec.md` is implemented | `traceability.md` | |
| Every acceptance criterion has a passing automated test | `acceptance-checklist.md` | |
| Nothing shipped that isn't in the spec (no scope creep) | diff review | |
| `usecase.md` API contract updated | | |

## Quality gates (CI)

| Gate | Threshold | Actual | ✅ |
|------|-----------|--------|:--:|
| Backend unit tests | all pass | | |
| Backend integration tests (real DB) | all pass | | |
| Frontend tests | all pass | | |
| Cross-backend parity (`port-endpoint` compare) | identical | | |
| Lint / format | clean | | |
| Coverage on changed files | ≥ (team bar) | | |
| Schema loads into a clean DB | no error | | |

## Change safety (brownfield only)

| Check | Evidence | ✅ |
|-------|----------|:--:|
| Full pre-existing test suite passed **before** the change | `regression-report.md` | |
| Full pre-existing test suite passes **after** the change | `regression-report.md` | |
| Every intentionally-changed test is justified in the report | | |
| Change stayed within the documented blast radius | `change-impact.md` | |

## Operational

| Check | Notes | ✅ |
|-------|-------|:--:|
| Rollback plan (revert PR? feature flag? data migration reversible?) | | |
| No secrets in the diff | | |
| Copilot code review run and comments resolved | PR link | |
| Human reviewer approved | PR link | |

## Verdict

- [ ] **Release-ready** — all of the above are ✅.
- [ ] **Not yet** — blockers:
