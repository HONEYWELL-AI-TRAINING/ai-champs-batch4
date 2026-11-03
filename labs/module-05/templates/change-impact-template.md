# Change-Impact Analysis — <change name>

Copy to `specs/<nnn>-<slug>/change-impact.md`. Fill it in **before** writing
code (Lab 02), using the archaeology note. This maps the **blast radius** — and
the blast radius, not the file you happen to edit, is the real scope of the
change.

## The change (innermost ring)

What is actually being modified — one or two sentences, specific:

> 

## Blast radius

### Ring 1 — Directly dependent (imports/calls the changed code, or its contract)

| File / module | How it depends | Needs a change? | Needs a new/changed test? |
|---------------|----------------|:---------------:|:-------------------------:|
| | | | |

### Ring 2 — Indirectly affected (depends on Ring 1, or shares state/schema/contract)

| File / area | Path of impact | Risk if ignored |
|-------------|----------------|-----------------|
| | | |

### Ring 3 — Believed unaffected (protected by regression tests)

| Area | Why it should be safe | Which existing test proves it |
|------|-----------------------|-------------------------------|
| | | |

## Cross-cutting checks

- [ ] Database schema: does `database/schema.sql` change? Migration implications?
- [ ] The other two backends: same change, same shape — listed as tasks?
- [ ] Existing seed data / fixtures: still valid?
- [ ] Existing API contract (`usecase.md`): does a documented behaviour change?
- [ ] Downstream features built on this (Module 03 stats, Module 04 comments):
      impact stated?
- [ ] Frontend: components, services, and their tests?

## Regression protection plan

| Existing behaviour that must be preserved | Existing test that guards it | Gap? add a test |
|-------------------------------------------|------------------------------|-----------------|
| | | |

## Change-impact summary (carry forward to the plan)

- Files in scope (Ring 1 + necessary Ring 2), total count:
- Files explicitly **out** of scope (and why):
- New regression tests to add before implementing:
- The single riskiest part of this change, and how it's mitigated:
