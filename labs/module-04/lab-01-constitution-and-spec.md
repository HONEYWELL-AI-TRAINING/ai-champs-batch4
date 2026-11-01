# Lab 01 — Constitution & Specification

**Time:** ~30 min · **Surface:** `specify` CLI + Copilot Chat ·
**Prereq:** Module 04 [set-up](README.md#set-up--do-this-once-before-lab-01) done

## Objective

Initialise Spec Kit in the Task Board repo, write a **constitution** that
encodes the project's non-negotiables, then turn [`feature-brief.md`](feature-brief.md)
into a structured `spec.md` and sharpen it with `/speckit.clarify` — until it is
unambiguous, testable, traceable, and complete.

## Why it matters for the enterprise

A prompt is interpreted fresh every time you send it. A specification is written
**once**, reviewed, versioned, and reused by every downstream step — plan, tasks,
implementation, tests, and the next engineer who touches the feature. The
constitution goes further: it is the set of rules that *every* spec on this repo
is checked against, so quality bars don't depend on who happens to be driving
Copilot that day.

## Background — the artifacts

| File | Created by | Contains |
|------|-----------|----------|
| `.specify/memory/constitution.md` | `/speckit.constitution` | Non-negotiable project principles |
| `specs/001-task-comments/spec.md` | `/speckit.specify` | Requirements, constraints, interfaces, acceptance criteria |
| `specs/001-task-comments/` (folder) | `/speckit.specify` | Branch + folder for this one feature |

Slash commands run **inside Copilot Chat** (Spec Kit installed them as prompt
files during `init`). Older Spec Kit uses bare names: `/constitution`,
`/specify`, `/clarify`.

---

## Step 1 — Initialise Spec Kit

From `labs/module-01/` (your workspace root):

**macOS / Linux**

```bash
specify init --here --integration copilot --script sh
```

**Windows (PowerShell)**

```powershell
specify init --here --integration copilot --script ps
```

- `--here` initialises in the current folder (don't create a subfolder).
- If it warns about existing files, allow it to proceed / pass `--force` — it
  adds `.specify/` and its own `.github/prompts/speckit.*.prompt.md`; it does
  **not** touch your Module 02/03 files.

**Offline fallback:** if `init` can't reach GitHub, clone
`github/spec-kit` once elsewhere and copy its `templates/` and `scripts/` into
`.specify/`, then create `.specify/memory/constitution.md` by hand from
`templates/constitution-template.md`. The slash commands are just prompt files —
you can copy those from `spec-kit/.github/prompts/` too.

Commit the scaffold:

```bash
git add .specify .github && git commit -m "Module 04: initialise Spec Kit"
```

## Step 2 — Write the constitution

In Copilot Chat:

```
/speckit.constitution

Principles for the Engineering Task Board. Derive them from
.github/copilot-instructions.md and CONTEXT.md, and add SDD-specific bars:

1. Layered architecture — Controller/Router → Service → Repository. All DB
   access and all aggregation live in the repository. Non-negotiable.
2. Single schema owner — database/schema.sql is the only place schema is
   defined. Schema changes are reviewed edits to that file. No migration tooling.
3. Error contract — 404 for a missing resource, 422 for a bad request body.
   No other codes on CRUD endpoints.
4. Cross-backend parity — .NET, Python, and Java expose every feature
   identically and return byte-identical JSON (timestamp key casing aside).
5. Tests-first-class — no task is done until it has tests in the same layer and
   they pass.
6. Spec is the source of truth — code changes for a requirement change start
   with a spec change, never ad hoc in chat or the editor.
7. Scoped context — implementation uses a compressed, task-scoped context brief
   (see .github/prompts/context-brief.prompt.md), not whole-repo dumps.
```

Review the generated `.specify/memory/constitution.md`. Edit anything vague —
this file gets cited on every later step, so it must be crisp. Commit it:

```bash
git add .specify/memory/constitution.md && git commit -m "Module 04 Lab 01: project constitution"
```

## Step 3 — Generate the specification

Feed the brief in. Reference the file so Copilot reads the whole thing:

```
/speckit.specify

Build the feature described in docs/feature-task-search.md — a task search on the Engineering Task Board. Honour the constitution. Do not decide
implementation details (framework, table columns beyond the obvious) — that is
for /speckit.plan.
```

Spec Kit creates a feature branch and `specs/001-task-comments/spec.md`. Open it.

## Step 4 — Clarify the ambiguities

```
/speckit.clarify
```

It asks structured questions — answer them from the "Open questions" list in the
brief. Suggested answers (use your judgement; the point is that the spec now
*records a decision*):

| Question | Decision to record |
|----------|--------------------|
| Body length limit | `body`: 1–1000 chars |
| Author length limit | `author`: 1–100 chars |
| `GET` for a missing task | `404` (consistent with the rest of the API) |
| Max comments per task | No limit for now |
| `POST` response body | The created comment only (`201`), not the whole thread |
| Ordering | Oldest first (ascending `created_at`) |
| Delete semantics | Hard delete; task deletion cascades |

Re-open `spec.md` — the clarifications should now be baked into requirements and
acceptance criteria, not left as open questions.

## Step 5 — Quality-check the spec

Score `spec.md` against the four qualities. Add a `## Self-review` section to the
spec (or a note in your PR) with the evidence:

| Quality | Check | Pass? |
|---------|-------|:-----:|
| **Unambiguous** | Could two engineers implement materially different things from this? Find one sentence that could be read two ways — fix it. | |
| **Testable** | Every acceptance criterion is mechanically checkable (a status code, a field, a count). Rewrite any that say "works well" / "is fast". | |
| **Traceable** | Requirements are numbered (`REQ-01…`) and acceptance criteria reference them (`AC-01 covers REQ-02`). | |
| **Complete** | Non-happy-path covered: missing fields, too-long fields, missing task, missing comment, task deletion. Non-functional: parity, layering, tests. | |

Optionally run `/speckit.checklist` to have Spec Kit generate a quality
checklist for the spec.

## Step 6 — Commit

```bash
git add specs/ && git commit -m "Module 04 Lab 01: task-comments spec + clarifications"
```

## Verify

- [ ] `.specify/memory/constitution.md` exists and states the 7 principles
      crisply.
- [ ] `specs/001-task-comments/spec.md` exists on a feature branch.
- [ ] No "open question" or `[NEEDS CLARIFICATION]` markers remain in `spec.md`.
- [ ] Requirements are numbered and acceptance criteria reference them.
- [ ] Every acceptance criterion is mechanically checkable.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `specify: command not found` | `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`, then reopen the terminal. |
| Slash commands don't appear in Chat | Reload VS Code. Check `.github/prompts/` has `speckit.*.prompt.md` files. Older installs: use `/specify` not `/speckit.specify`. |
| `init` refuses — folder not empty | Pass `--force`; it merges, it doesn't wipe. Commit your work first so you can see its diff. |
| Spec is thin / generic | You didn't reference `feature-brief.md` by path, or the constitution is vague. Fix the constitution, re-run `/speckit.specify`. |
| `/speckit.clarify` asks nothing | The spec may already be over-specified with guesses. Check those guesses are decisions you'd defend; adjust the spec directly. |

## Recap & carry-forward

You have a constitution and a clarified specification. **Lab 02** turns the spec
into an architecture `plan.md` and a `tasks.md` of small, verifiable units — and
starts the traceability matrix.
