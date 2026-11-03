# Lab 02 — Govern It, Then Hand It Over

**Time:** ~30 min · **Surface:** Rovo Studio + the repo ·
**Prereq:** Lab 01 complete (a tested draft workflow + `workflow-spec.md` + `test-log.md`)

## Objective

Turn the working draft from Lab 01 into a **publishable, owned** workflow: review
its permission-aware access and data boundary, version and publish it as v1.0,
name a business owner and a technical owner, and produce the **handoff note** that
crosses the governance boundary to the technical owner — without the business
author bypassing governance.

## Why it matters for the enterprise

A workflow that only its author understands is a liability the day they change
teams. Governance review + explicit ownership + a version history make it a
shared asset: reviewable, reversible, and safe to run on real project data. The
handoff is the moment the organisation — not one person — owns the automation.

## Background — what "published" carries with it

| Concern | What it means here |
|---------|--------------------|
| **Permission-aware access** | The workflow sees and acts only within the running identity's entitlements — never broader than the author |
| **Business/technical collaboration** | Business authors and tests; a technical owner reviews and takes runtime ownership — the author does **not** self-approve a production runtime |
| **Versioning** | v1.0 is a fixed, reviewable artifact; changes are proposed, reviewed, and reversible |
| **Ownership** | One named business owner, one named technical owner, a named approver |
| **Governance boundary** | Coordination stays in the workflow; engineering execution (PRs, merges) stays behind the Module 08 gate |

---

## Step 1 — Complete the governance review

Open `workflows/release-digest/governance-review.md`. Fill every section using
what Lab 01 actually did:

- **§1 Identity:** decide — does it run as the *invoking user* or a *scoped
  service account*? For a report that publishes to a shared space, a scoped
  service account is usually right; write down exactly which Jira projects and
  Confluence spaces that account can touch, and confirm it's **not broader** than
  the author's own access.
- **§2 Data boundary:** fill the table from `workflow-spec.md` §4. Add the
  mitigation for any output that could leak internal Jira notes into a wider
  summary (e.g. "digest is built from story titles + acceptance criteria only,
  never from internal comments").
- **§3 Approval:** confirm the approver ≠ author, and that the approval is
  recorded against the workflow version.
- **§4 Versioning:** version is `v1.0.0`; create the change log (Step 3).
- **§5 Ownership:** name the business owner (you / the RTE) and leave the
  technical owner line for Step 4 to confirm.
- **§6 Governance boundary:** state what the technical owner may change alone
  (connectors, runtime identity, tracing) vs what returns to the author (the
  scenario, the wording, the approval routing).
- **§7 Sign-off:** business owner ticks now; technical owner ticks at handoff.

Cross-check against Module 07's `specs/002-task-soft-delete/mcp-governance.md` —
the connected-source rules there apply to this workflow's `specs/` grounding too.

## Step 2 — Tighten the workflow to match the review

If the governance review surfaced anything (grounding broader than needed, an
action that could run pre-approval, an output field that leaks), fix it in the
Studio config **and** in `workflow-spec.md`. Re-run the Lab 01 Scenario 4
fail-safe test one more time. Note the change in `test-log.md`.

## Step 3 — Version and publish

**[Studio]** Publish the workflow as **v1.0.0**. In the publish notes, link the
spec and governance review by path.

Create the change log:

```md
<!-- workflows/release-digest/CHANGELOG.md -->
# Changelog — Release Digest workflow

## v1.0.0 — <date>
- First published version.
- Trigger: soft-delete epic → Ready for Release (+ manual).
- Grounding: soft-delete epic + stories; "Task Board — Release Notes" Confluence
  page; specs/002 (read-only).
- Approval checkpoint: RTE, after drafts, before publish.
- Non-goals enforced per workflow-spec.md §8.
```

**[Spec]** No Studio? "Publish" = tag the spec: add a `Version: 1.0.0` line at the
top of `workflow-spec.md` and freeze it; changes go through a PR from here on.

## Step 4 — Write the handoff note

Open `workflows/release-digest/handoff-note.md` and fill it in. The "what I need
from the technical owner" checklist is the real content:

- confirm the runtime identity and that connected sources match org policy
- confirm the approval checkpoint cannot be skipped in the target runtime
- take ownership of connectors + incident response (add themselves to
  `governance-review.md` §5)
- wire **Module 10 (Agent Prism)** tracing before promoting past pilot

Then walk it through with whoever plays the technical owner (an instructor, a
peer, or your platform lead). They tick `governance-review.md` §7.

## Step 5 — Commit

```bash
git add workflows/release-digest/
git commit -m "Module 09 Lab 02: governance review + v1.0 publish + handoff note"
git push
```

Optionally open a PR merging `module-09-studio` into `main` so the `workflows/`
folder is on the default branch for Module 10.

## Verify

- [ ] `governance-review.md` is complete: identity, data boundary, approval,
      versioning, ownership, governance boundary — all filled, business owner
      signed.
- [ ] The runtime identity is documented and confirmed **not broader** than the
      author's access.
- [ ] The workflow is published as **v1.0.0** with a `CHANGELOG.md` (or the spec
      is frozen at v1.0.0).
- [ ] `handoff-note.md` names a technical owner and lists what they must confirm.
- [ ] A technical-owner stand-in has reviewed and signed §7.
- [ ] The non-goals still hold — nothing in the published workflow crosses into
      code, PRs, or the Module 08 merge gate.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Can't decide invoking-user vs service account | Publishing to a shared space → service account with a documented, minimal scope. Personal ad-hoc reports → invoking user. Write the reasoning in §1. |
| Technical owner won't accept the handoff | Usually a missing item — unclear runtime identity, no tracing plan, or connectors outside policy. Close the checklist gaps and re-present. |
| Author is also the only possible approver | Acceptable for a pilot **if** recorded as a known limitation in `handoff-note.md`; the technical owner's first task is to nominate a separate approver. |
| No Module 10 / Agent Prism yet | Note it as a pre-promotion dependency in the handoff — the workflow stays at pilot scope until tracing is wired. |
| Versioning feels heavy for one workflow | It's the habit that scales. v1.0 + a two-line changelog entry is the whole cost. |

## Recap — Module 09 complete

`workflows/release-digest/` now holds:

```
workflow-spec.md      # Lab 01 — trigger, grounding, actions, checkpoint, non-goals, tests
test-log.md           # Lab 01 — four scenarios incl. fail-safe
governance-review.md  # Lab 02 — identity, data boundary, versioning, ownership, boundary
handoff-note.md       # Lab 02 — what the technical owner confirms and owns
CHANGELOG.md          # Lab 02 — v1.0.0
```

A non-technical author has grounded an agent on permission-aware project data,
placed a human checkpoint where it belongs, and handed a versioned, owned
workflow to a technical owner — coordination automated, governance intact.

**Module 10** points **Agent Prism** at this workflow and the engineering agents
together: the same traces, failures, drift, and token/cost view across both. The
run cost it captures feeds Module 11's ROI model.
