# Workflow Spec — <workflow name>

Copy to `workflows/<slug>/workflow-spec.md`. This is the authored design of the
studio workflow: what starts it, what it reads, what it does, where a human
confirms, and what it must never do. It doubles as the **[Spec]** deliverable
when Rovo Studio isn't available.

## 1. Purpose (one sentence)

<What exists when this workflow has run — e.g. "A drafted release digest and
program-status summary for the soft-delete epic, waiting for RTE approval.">

## 2. Business owner & scenario

| | |
|--|--|
| Scenario | program reporting / issue triage / release coordination |
| Business owner (author) | <role — e.g. RTE> |
| Who consumes the output | <e.g. program stakeholders, release manager> |
| Runs how often | <schedule / on Jira event / manual> |

## 3. Trigger

| | |
|--|--|
| Type | Jira event · schedule · manual run |
| Exact condition | <e.g. "Epic in project TB transitions to *Ready for Release*"> |
| Who can invoke it | <role / group> |

## 4. Grounding (permission-aware view)

The data the agent reasons over. List only what the workflow actually needs.

| Source | Scope (project / space / label) | Read or write | Why it's needed |
|--------|--------------------------------|:-------------:|-----------------|
| Jira | <project TB, epic + children> | read | scope & status of the feature |
| Confluence | <space REL, page "Task Board — Release Notes"> | read + draft | the doc the digest is written into |
| Repo specs (via connected source / MCP, read-only) | `specs/002-task-soft-delete/` | read | authoritative acceptance criteria |
| … | | | |

Rejected sources (available but not grounded), and why:
- <e.g. "The codebase itself — this workflow reports, it doesn't review code.">

## 5. Actions & steps

Numbered. Each step: what it does, which grounding it uses, and the connector.

| # | Step | Uses | Connector / action | Output of the step |
|---|------|------|--------------------|--------------------|
| 1 | Summarise epic scope & status | Jira grounding | Jira read | scope/status text |
| 2 | Cross-check against acceptance criteria | repo specs | read | coverage note (done / open) |
| 3 | Draft the release digest | steps 1–2 | — | digest draft |
| 4 | Draft the program-status summary | steps 1–2 | — | program summary draft |
| 5 | Write drafts to Confluence as a **draft** page + comment on the Jira epic | steps 3–4 | Confluence write (draft), Jira comment | draft page URL, epic comment |
| 6 | Notify the approver | — | Slack/Teams/email | approval request |

## 6. Approval flow / human-in-the-loop checkpoint

| | |
|--|--|
| Checkpoint sits **after** step | 5 (drafts created, nothing published) |
| Who approves | <role — e.g. RTE or Release Manager> |
| What they see | the draft digest + program summary + the coverage note |
| On **approve** | publish the Confluence page, post the digest as an epic comment, mark done |
| On **reject** | return to step 3 with the reviewer's notes; do not publish |
| Timeout / no response | <e.g. "hold as draft, re-notify after 1 business day"> |

## 7. Output

| Deliverable | Where it lands |
|-------------|----------------|
| Release digest | published Confluence page section + Jira epic comment |
| Program-status summary | <e.g. posted to the program channel> |

## 8. Non-goals — the governance boundary

This workflow must **never**:
- edit code, open, review, or merge a pull request
- transition a Jira issue without the approval checkpoint
- publish anything before approval
- act on Jira projects / Confluence spaces outside its grounded scope
- bypass the Module 08 PR quality gate — engineering execution stays with the
  engineering agents (Modules 02–08)

## 9. Test cases (fill during Lab 01)

| # | Scenario | Expected behaviour | Result |
|---|----------|--------------------|--------|
| 1 | Happy path — epic ready, all stories done | correct digest, checkpoint fires, publishes on approve | |
| 2 | One story still In Progress | digest flags the gap; program summary shows it as at-risk | |
| 3 | Approver rejects with a note | no publish; redraft incorporates the note | |
| 4 | Grounding denied (no access to the space) | fails safe with a clear message; no partial publish | |
