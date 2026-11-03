# PR Automation Report — <feature / change>

Copy to `specs/<nnn>-<slug>/pr-automation-report.md`. Run the full flow against
one deliberately flawed PR and one clean PR, and compare.

## The two PRs

| | Flawed PR | Clean PR |
|--|-----------|----------|
| Branch / PR # | | |
| What's in it | (see `flawed-change.md`) | a real, correct change |
| Known issues planted | | none |

## Stage-by-stage results

| Stage | Flawed PR | Clean PR |
|-------|-----------|----------|
| Quality gate (CI) — pass/fail + which checks | | |
| Copilot code review — # comments, did it name the real issues? | | |
| LLM-as-Judge — scores J1–J6, overall, confidence | | |
| Judge decision — fast-track / escalate | | |
| Correct decision? | | |

## Did the flaws get caught?

| Planted flaw | Caught by (stage) | Evidence quality (specific file:line + rule? or vague?) |
|--------------|-------------------|--------------------------------------------------------|
| 1 | | |
| 2 | | |
| 3 | | |

Any flaw not caught → the gate or the rubric has a hole. Note the fix.

## Review-cycle measurement

| Metric | Manual baseline (estimate) | With the automated gate + judge |
|--------|----------------------------|---------------------------------|
| Time from PR open → ready for human decision | | |
| Human review time (minutes) | | |
| Back-and-forth round trips | | |
| Issues found before a human looked | 0 | |

## Loop closed

- [ ] The flawed PR was correctly **escalated**; a human reviewed and requested
      changes citing the judge's evidence.
- [ ] The clean PR was **fast-tracked**; a human did a light approval.
- [ ] False positives / negatives noted, with a rubric or gate adjustment.

## Takeaway

Where did automation save time, and where did it (correctly) defer to a human?
