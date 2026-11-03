# Defect-Injection Report — <feature name>

Copy to `specs/<nnn>-<slug>/defect-injection-report.md`. A test strategy you
haven't seen catch anything is a hypothesis. Inject known defects, prove each is
caught, and record where and how fast.

## Method

- Branch: `m06-defect-injection` (throwaway — never merged)
- Baseline: full suite green before any injection (record counts)
- One defect at a time: inject → run suite → record → revert → next

## Injected defects

| # | Defect (what you broke, file:line) | Which AC it violates | Caught by (test name) | Pyramid layer | Time to detection | Caught? |
|---|-----------------------------------|----------------------|-----------------------|---------------|-------------------|:-------:|
| 1 | | | | unit / integration / contract / e2e | (test run seconds) | |
| 2 | | | | | | |
| 3 | | | | | | |

## Defects NOT caught (if any)

| # | Defect | Why the suite missed it | New test added (name) | Now caught? |
|---|--------|-------------------------|-----------------------|:-----------:|
| | | | | |

Any miss is the real finding — it means an acceptance criterion had no real
test, or the test was at the wrong layer.

## Cost-avoided framing (feeds Module 11)

For each defect, estimate: if this had shipped, where would it have been found
(staging / prod / customer), and what would that have cost (rough: eng hours to
diagnose + fix + hotfix release, × the number of people)? The test that caught
it in seconds is that cost, avoided.

| Defect | Likely escape point if untested | Rough cost avoided |
|--------|--------------------------------|--------------------|
| 1 | | |

## Verdict

- [ ] Every injected defect was caught by a specific, named test.
- [ ] Any miss has a new test and is now caught.
- [ ] The strategy's weakest layer is identified: __
