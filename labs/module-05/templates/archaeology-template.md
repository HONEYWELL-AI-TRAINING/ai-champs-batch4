# Repository Archaeology — <change name>

Copy to `specs/<nnn>-<slug>/archaeology.md`. Fill it in **before** writing any
code (Lab 02). The goal is to understand what exists well enough that "minimal
change" has a concrete meaning for *this* codebase.

## 1. Architecture & dependencies

| Question | Finding | Evidence (file:line) |
|----------|---------|----------------------|
| What are the layers, and what does each own? | | |
| How does a request flow end to end for the area I'm changing? | | |
| What external dependencies are involved (DB, libraries)? | | |
| Where is configuration read from? | | |

## 2. Existing design patterns

| Pattern in use | Where | Do I have to follow it? |
|----------------|-------|-------------------------|
| (e.g. repository returns domain objects, service maps DTOs) | | |
| (e.g. errors raised as exceptions, mapped centrally) | | |
| (e.g. query filters built in the repository) | | |

## 3. API contracts affected

| Endpoint | Current behaviour | Documented where |
|----------|-------------------|------------------|
| | | `usecase.md` / `spec.md` |

## 4. Existing tests around the change area

| Test file | What it pins down | Would my change break it? |
|-----------|-------------------|---------------------------|
| | | |

List the exact tests that assert the *current* behaviour you're about to change
— these are the ones that will (correctly) fail and need updating, versus the
ones that must keep passing untouched.

## 5. Coding conventions

- Naming: 
- File/module layout: 
- Test naming & structure: 
- Anything the linter/formatter enforces: 

## 6. Archaeology summary (the part you carry forward)

- The 3–5 files that are the true centre of this change:
- The pattern the change must follow:
- The existing behaviour the change modifies (state it precisely):
- Tests that will need updating vs tests that must not move:
