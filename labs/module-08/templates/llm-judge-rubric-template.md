# LLM-as-Judge Rubric — PR Quality

Copy to `.github/pr-judge-rubric.md`. The judge scores a PR **and the AI review
of it** against these criteria, reports a confidence level, and escalates to a
human when confidence is low or any criterion fails.

## Criteria (score each 0–2)

| # | Criterion | 0 — fail | 1 — concern | 2 — pass |
|---|-----------|----------|-------------|----------|
| J1 | **Spec compliance** | a requirement is unmet or misimplemented | minor deviation, not documented | every acceptance criterion met, cited |
| J2 | **Coding / design standards** | violates the constitution (layering, error contract, schema ownership) | a borderline call | follows the constitution and local conventions |
| J3 | **Security** | a secret, injection, unsafe input handling, or risky dependency | a hardening opportunity | no security concern |
| J4 | **Test evidence** | changed behaviour with no test, or tests don't run | tests exist but coverage/edge-cases thin | every changed behaviour has a passing test at the right layer |
| J5 | **Regression risk (brownfield)** | pre-existing suite not run, or a test silently changed | changed tests justified but risk noted | full suite green before+after, changes justified |
| J6 | **Maintainability** | unexplained complexity, dead code, scope creep | readable but could be tighter | clear, minimal, in scope |

## Verdict rules

- **Overall score** = sum (max 12).
- **PASS** requires: every criterion ≥ 1, no criterion = 0, overall ≥ 10.
- **Confidence** = HIGH / MEDIUM / LOW — how sure the judge is of its own scores,
  given how much context it had (spec present? tests runnable? diff small enough
  to reason about?).

## Escalation

Escalate to a **human reviewer** if ANY of:
- any criterion scored 0
- J3 (security) scored below 2
- confidence is LOW
- the AI review and the judge disagree materially

Otherwise: **fast-track** — human does a light approval, trusting the evidence.

## Output format

```
## LLM-as-Judge — PR #<n>  (rubric v<x>)
| J1 | J2 | J3 | J4 | J5 | J6 | Overall |
Confidence: HIGH | MEDIUM | LOW  — because <reason>
Verdict: PASS | FAIL
Decision: FAST-TRACK | ESCALATE TO HUMAN  — because <reason>
Evidence:
- J1: <file:line / spec ref>
- ...
Notes for the human (if escalating):
```
