# Lab 07 — Automated Copilot Code Review

**Time:** ~15 min · **Surface:** GitHub.com pull requests (+ VS Code) ·
**Prereq:** Lab 06 (repo on GitHub with instruction files on the default branch)

## Objective

Get Copilot to review Task Board pull requests automatically, tune what it
comments on with **path filters** and **review instructions**, and see how the
`copilot-instructions.md` from Lab 01 shapes the feedback.

## Why it matters for the enterprise

Automated review catches the mechanical issues — missed error cases, layer
violations, absent tests — *before* a human reviewer spends attention on them.
It makes review coverage consistent across every PR and every repo, and it
enforces the same rules the IDE Copilot follows, so feedback doesn't contradict
itself.

## Background

- Request a review from **Copilot** on any PR (Reviewers → Copilot), or make it
  automatic for a repo/org via **rulesets** or the repo's Copilot settings.
- Copilot code review reads `.github/copilot-instructions.md` and path-specific
  `.github/instructions/*.instructions.md`.
- **`.github/copilot-instructions.md` review-guidance** and, in newer versions, a
  dedicated review config let you steer tone and focus, and **exclude paths**
  (generated code, vendored files, `dist/`).

---

## Step 1 — Make it automatic for the repo

On GitHub.com: **Repository → Settings → Rules → Rulesets → New branch ruleset**
(target your default branch) → enable **Request pull request review from
Copilot**. Alternatively, some orgs expose a simpler toggle under
**Settings → Copilot → Code review → Automatic review**.

If your org doesn't allow that, you'll request reviews manually in Step 4 —
everything else in the lab still applies.

## Step 2 — Add path exclusions and review focus

Copilot review honours a review-instructions file. Create it:

```md
<!-- .github/instructions/code-review.instructions.md -->
---
applyTo: "**"
---
# Copilot code review — focus and exclusions

## Do not review these paths
- `**/dist/**`, `**/bin/**`, `**/obj/**`, `**/target/**`
- `**/*.lock`, `**/package-lock.json`
- `frontend/public/**`

## Prioritise, in order
1. **Architecture:** SQL or DB access outside a repository; validation or
   business rules in a controller/router; `fetch` in a React component.
2. **Error contract:** any status code other than `200/201/204/404/422` on the
   task endpoints; `404` vs `422` used incorrectly.
3. **Schema ownership:** new migrations, `create_all`, `ddl-auto` != `none`,
   edits to `database/schema.sql` not called for by the PR description.
4. **Tests:** changed behaviour with no new or updated test; a test that hits a
   real database instead of the fixtures.
5. **Cross-backend drift:** a change to one backend that isn't reflected in the
   contract or portable to the others.

## Style
Terse. One comment per issue, with the file:line and the smallest fix. No
summaries of what the code does. Don't comment on formatting.
```

Commit and push to the default branch.

## Step 3 — Open a PR with a deliberate flaw

From a new branch, introduce one clear violation — e.g. in the Python backend,
put a raw SQL query directly in `routers/tasks.py`, or return `400` for a
missing title instead of `422`.

**macOS / Linux**

```bash
git checkout -b demo/bad-layering
# make the edit in your editor
git commit -am "Add task search (raw SQL in router)"
git push -u origin demo/bad-layering
gh pr create --fill
```

**Windows (PowerShell)** — identical commands (`gh` and `git` are cross-platform).

## Step 4 — Get the review

If automatic review isn't on:

```bash
gh pr edit <pr-number> --add-reviewer "@copilot"
```

Within a minute Copilot posts review comments. Confirm it flags:

- [ ] The SQL / DB access in the router (architecture rule).
- [ ] The wrong status code, if you added one (error-contract rule).
- [ ] A missing test for the new behaviour.
- [ ] **Nothing** about files under `dist/` or `package-lock.json`.

## Step 5 — Compare with and without instructions

To see the instruction file's effect: on a scratch branch, temporarily rename
`.github/copilot-instructions.md`, push, open a similar PR, and request review
again. The comments become generic ("consider extracting this", "add error
handling") instead of citing *your* layer and contract rules. **Restore the file
afterwards.**

## Step 6 — Act on the review, then merge clean

Fix the flaw (move the query to the repository, restore `422`, add the test),
push, and confirm Copilot's follow-up review resolves its comments. Then close
the demo PR without merging (it was only for the exercise) — or fix it properly
and merge.

## Verify

- [ ] `.github/instructions/code-review.instructions.md` is on the default
      branch.
- [ ] A PR with a layer violation gets a Copilot comment naming the rule.
- [ ] Excluded paths get no comments.
- [ ] Removing `copilot-instructions.md` visibly degrades review specificity.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No Copilot reviewer option | Copilot code review not enabled for the org/repo — ask your admin. |
| Review is generic | Confirm `.github/copilot-instructions.md` is on the PR's **base** branch, not just the feature branch. |
| Comments on generated files | Check the `applyTo`/exclusion globs; they match paths relative to repo root. |
| Too noisy | Tighten the "Style" section — "one comment per issue", "don't comment on formatting" — and re-request review. |

## Recap & carry-forward

Both sides of the delivery loop are now automated and governed: the coding agent
proposes, Copilot review checks, a human approves. **Lab 08** moves to the
terminal — Copilot CLI — and to authoring the CI workflow that all of this
depends on.
