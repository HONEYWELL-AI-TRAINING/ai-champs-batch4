# Test Strategy — <feature name>

Copy to `specs/<nnn>-<slug>/test-strategy.md`. A test strategy is **derived** from
the spec, not chosen from a menu: each acceptance criterion maps to the kind of
test that can actually prove it.

## 1. Source

- Spec: `specs/<nnn>-<slug>/spec.md`
- Acceptance criteria count: __
- Existing tests for this feature area: __ (list files)

## 2. Criterion → test-type mapping

| AC | Criterion (from spec) | Test type | Why this type proves it | Test name (planned) | Exists? |
|----|-----------------------|-----------|-------------------------|---------------------|:-------:|
| AC-01 | | unit / integration / contract / e2e | | | |

**Rule:** every AC has at least one row. Every planned test maps to an AC.

## 3. The pyramid for this feature

| Layer | Count | What lives here | Runtime budget |
|-------|-------|-----------------|----------------|
| Unit | | isolated logic, validation, mapping | ms |
| Integration (Testcontainers) | | real DB: queries, constraints, cascades, tx | seconds |
| API / contract | | the HTTP contract in `usecase.md` is honoured | seconds |
| End-to-end | | one or two full user flows | tens of seconds |

## 4. Test data design (4 categories)

| Category | For this feature, that means… | Tests that use it |
|----------|-------------------------------|-------------------|
| Happy path | | |
| Boundary & edge | (empty, max length, off-by-one, N=0, N=1) | |
| Negative & invalid | (malformed body, unknown status, missing task) | |
| Failure & timeout | (DB constraint violation, connection dropped, cascade) | |

## 5. Gaps found in the current suite

- Unmapped acceptance criteria (no test proves them):
- Orphan tests (test with no acceptance criterion behind it — delete or spec it):
- Behaviour tested at the wrong layer (e.g. a DB constraint checked only with a mock):

## 6. Coverage target

- Changed-file line coverage bar: __%
- Every AC → green test before the feature is "validated".
