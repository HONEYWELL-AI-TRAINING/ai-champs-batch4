# Lab 01 — Ground an Agent and Build the Workflow

**Time:** ~30 min · **Surface:** Atlassian Rovo Studio (or the spec, if no access) ·
**Prereq:** Module 09 [set-up](README.md#set-up--do-this-once-before-lab-01) done

## Objective

Author a studio workflow in Rovo Studio that turns *"the soft-delete epic is
ready for release"* into a **drafted release digest and program-status summary**,
grounded on a permission-aware view of Jira and Confluence, with a **human
approval checkpoint** before anything is published. Capture the design in
`workflow-spec.md` and test it against sample data.

## Why it matters for the enterprise

The people who need program reports and release coordination — POs, TPOs, RTEs —
are not the people writing code. Giving them a governed place to *author* the
coordination logic means the report is consistent, grounded in real project
data, and produced without pulling an engineer off delivery. The approval
checkpoint is what makes it safe to let an agent draft in the first place.

## Background — the five elements

| Element | In this workflow |
|---------|------------------|
| **Trigger** | The soft-delete epic transitions to *Ready for Release* (also allow a manual run) |
| **Grounding** | The Jira epic + its stories; the Confluence "Task Board — Release Notes" page; `specs/002-task-soft-delete/` read-only |
| **Actions & connectors** | Summarise scope/status, cross-check acceptance criteria, draft the digest + program summary, write them as a Confluence **draft** + a Jira comment, notify the approver |
| **Approval checkpoint** | RTE reviews the drafts; approve → publish, reject → redraft with notes |
| **Output** | Published release digest (Confluence + epic comment) and a program-status summary |

---

## Step 1 — Fill the workflow spec first

Open `workflows/release-digest/workflow-spec.md` (copied in set-up). Fill
**§1–§8 now**, before touching Studio — the spec is the design, Studio is the
build. Decisions to make explicitly:

- **§3 Trigger:** Jira event *plus* manual. Who can invoke — the RTE and the PO.
- **§4 Grounding:** the epic + children, one Confluence page, `specs/002` read
  only. Everything else (the codebase, other projects, other spaces) goes in the
  "rejected sources" list with a reason.
- **§6 Approval:** checkpoint sits **after drafts are written, before publish**.
  Approver is the RTE, and must not be the workflow's author.
- **§8 Non-goals:** copy the list from the template — no code, no PRs, no
  un-approved issue transitions, no acting outside grounded scope.

This filled spec is the **[Spec]** deliverable. If you have no Studio access,
also write §5 as a numbered prose runbook and skip to Step 4.

## Step 2 — [Studio] Create the agent and ground it

In Rovo Studio ([what is Rovo Studio](https://support.atlassian.com/rovo/docs/what-is-rovo-studio/)):

1. **New agent / workflow.** Name it `Release Digest — Task Board`.
2. **Instructions:** paste a short brief:
   ```
   You coordinate release reporting for the Task Board program. You draft; you
   never publish without approval. Ground every statement in the Jira epic, its
   stories, the linked Confluence release page, and the specs/002-task-soft-delete
   acceptance criteria. If a fact isn't in the grounded sources, say so — don't
   guess. You never edit code or pull requests.
   ```
3. **Grounding / knowledge sources:** add **only**
   - the Jira project, scoped to the soft-delete epic and its children
   - the Confluence space, scoped to "Task Board — Release Notes"
   - the repo `specs/` as a connected source (read-only) if your org exposes it
     via the Module 07 governed connection; otherwise attach the spec as a
     Confluence page and note the substitution in `workflow-spec.md` §4.
4. Confirm the grounding is **permission-aware** — it inherits what the running
   identity can see. Don't grant the agent broader access than the author has.

## Step 3 — [Studio] Configure the trigger, actions, and checkpoint

1. **Trigger:** Jira "issue transitioned" → epic → *Ready for Release*; also
   enable manual run.
2. **Steps** (match `workflow-spec.md` §5):
   - summarise epic scope & status from the Jira grounding
   - cross-check each acceptance criterion in `specs/002` → *done / open*
   - draft the **release digest** (what shipped, what's deferred, known issues)
   - draft the **program-status summary** (on-track / at-risk, blockers)
   - **action:** create a Confluence **draft** page update + a comment on the
     Jira epic with both drafts
3. **Approval checkpoint** after the draft step: route to the RTE with the two
   drafts and the coverage note. Configure:
   - **approve** → publish the Confluence page, post the digest as an epic
     comment
   - **reject** → loop back to the draft step with the reviewer's comment as
     input; nothing is published
4. **Notify:** send the approval request to the approver (Slack/Teams/email).

Save as a **draft** workflow — do not publish yet (that's Lab 02).

## Step 4 — Test against the sample data

Run the workflow (manual trigger) against your sample epic. Fill
`workflow-spec.md` §9:

| # | Scenario | How to set it up | Expected |
|---|----------|------------------|----------|
| 1 | Happy path | all stories *Done* | digest lists all 4 items shipped; checkpoint fires; approve → page publishes |
| 2 | Gap | set one story back to *In Progress* | digest flags it as deferred; program summary marks the epic **at-risk** |
| 3 | Reject loop | approver rejects with "add rollback note" | no publish; re-draft includes a rollback note |
| 4 | Access denied | temporarily remove your access to the Confluence space (or simulate in the **[Spec]** dry-run) | workflow fails safe with a clear message; **nothing** partially published |

For each: record what actually happened in the Result column. If behaviour
differs from the spec, fix the **spec** first, then the Studio config — the spec
stays the source of truth.

## Step 5 — Write the test log

```md
<!-- workflows/release-digest/test-log.md -->
# Test log — Release Digest workflow

Date: __________   ·   Built in: Rovo Studio / spec-only
Sample data: Jira epic __________ , Confluence page __________

| # | Scenario | Expected | Actual | Pass? | Fix made |
|---|----------|----------|--------|:-----:|----------|
| 1 | Happy path | | | | |
| 2 | Story still in progress | | | | |
| 3 | Approver rejects | | | | |
| 4 | Grounding access denied | | | | |

## Notes
- Did any output include data the recipient shouldn't see? →
- Did the workflow ever act before the checkpoint? (must be no) →
- Grounding that turned out unnecessary (remove it): →
```

## Step 6 — Commit

```bash
git add workflows/release-digest/workflow-spec.md workflows/release-digest/test-log.md
git commit -m "Module 09 Lab 01: release-digest studio workflow spec + test log"
```

## Verify

- [ ] `workflow-spec.md` §1–§9 are filled, including rejected grounding sources
      and the full non-goals list.
- [ ] The workflow drafts to Confluence + a Jira comment and stops at the
      approval checkpoint — it never publishes on its own.
- [ ] All four test scenarios were run and recorded in `test-log.md`, including
      the fail-safe (Scenario 4).
- [ ] Reject loops back to redraft without publishing.
- [ ] Nothing about code, PRs, or issue transitions happens without a human.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Agent invents story statuses or dates | Grounding scope is too broad or a source is missing — narrow it to the epic; add the "if it isn't grounded, say so" line to the instructions. |
| Workflow publishes before approval | The checkpoint is after the wrong step. It must sit between *draft* and *publish*, and the publish action must be on the **approve** branch only. |
| No `specs/` connected source available | Attach `specs/002` content as a Confluence page for now; note it in §4 and raise the connection need in the Lab 02 handoff. |
| Can't scope grounding to one epic | Scope to the project + a label you add to the epic's stories; record the label in §4. |
| No Rovo Studio access at all | Do every step as **[Spec]**: §5 as a runbook, Step 4 as a paper dry-run against the sample data. The artifacts and Lab 02 are unchanged. |

## Recap & carry-forward

You have a grounded, checkpoint-gated workflow and a test log proving it drafts
safely. **Lab 02** reviews its permissions, versioning, and ownership, publishes
it as v1.0, and hands it to a technical owner across the governance boundary.
