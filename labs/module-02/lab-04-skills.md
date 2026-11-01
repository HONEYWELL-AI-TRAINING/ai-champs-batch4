# Lab 04 — Agent Skills (Reusable Capability Packages)

**Time:** ~25 min · **Surface:** Copilot CLI / coding agent / agent mode ·
**Prereq:** Lab 03 complete

## Objective

Package a piece of Task Board engineering know-how — *"how we port a feature from
one backend to another so the JSON stays byte-identical"* — as a **skill**: a
folder with a `SKILL.md`, a reference note, and a helper script. The agent
discovers it by description and pulls it in **only when a task matches**. You
will build one skill fully and add a second as a challenge.

## Why it matters for the enterprise

Instructions (Lab 01) are always on. Prompt files (Lab 02) and chat modes
(Lab 03) are things a person chooses. A **skill** is the missing piece:
model-invoked, self-contained, and it can bundle **scripts and data**, not just
text. It turns "ask Priya, she knows how we do cross-backend ports" into a
versioned artifact every agent surface can use. Progressive disclosure means you
can ship many skills without bloating every prompt — only the one-line
description is always in context; the body and files load on demand.

## Background — how a skill is structured

```
.github/skills/
└── port-endpoint/
    ├── SKILL.md            # YAML frontmatter (name, description) + instructions
    ├── contract-notes.md   # reference the skill tells the agent to read
    └── scripts/
        ├── compare-responses.sh    # bundled helper (macOS / Linux)
        └── compare-responses.ps1   # bundled helper (Windows)
```

| Part | Loaded | Purpose |
|------|--------|---------|
| `description` (frontmatter) | Always | Lets the agent decide if the skill is relevant |
| `SKILL.md` body | When the skill is triggered | The actual procedure |
| Bundled files | When the body references them | Detail, data, runnable scripts |

> **Portability.** The `SKILL.md` format is shared across agent tools. GitHub
> Copilot discovers repo skills under `.github/skills/`; Claude Code / other
> agents look in `.claude/skills/` or a configured path. The *format* and the
> *idea* are stable; if your Copilot build doesn't auto-discover yet, you invoke
> it explicitly (Step 5) — the skill file is still the single source of truth.

---

## Step 1 — Create the skill folder

**macOS / Linux**

```bash
mkdir -p .github/skills/port-endpoint/scripts
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force -Path .github\skills\port-endpoint\scripts | Out-Null
```

## Step 2 — Write `SKILL.md`

```md
<!-- .github/skills/port-endpoint/SKILL.md -->
---
name: port-endpoint
description: >-
  Port a Task Board endpoint or feature from one backend (.NET, Python, or Java)
  to another so both return byte-identical JSON for the same request. Use when a
  change exists in one backend and must be mirrored in another, or when checking
  cross-backend parity.
---

# Port a Task Board endpoint between backends

## When to use
- A feature or endpoint exists in one backend and must be added to another.
- You need to verify two backends agree on the same request/response.

## Procedure
1. **Read the source.** In the source backend, read all three layers for the
   feature: repository (DB access), service (rules), controller/router (HTTP).
   Note every status code and response field.
2. **Read the target's idioms.** Open the equivalent layer files in the target
   backend. Match its framework style, error-mapping pattern, and test setup.
3. **Reproduce layer by layer**, obeying `.github/copilot-instructions.md`:
   repository query first, then service, then controller/router. No SQL outside
   the repository. No schema change.
4. **Match the JSON contract exactly**, with the ONE documented exception in
   `contract-notes.md` (timestamp key casing). Same field names, types, null
   handling, array ordering, and error-body shape otherwise.
5. **Mirror the tests.** Recreate the source backend's test cases in the target
   backend's framework (see `.github/instructions/tests.instructions.md`).
6. **Verify with the bundled script.** Start both backends, then run
   `scripts/compare-responses.sh <path>` (macOS/Linux) or
   `scripts/compare-responses.ps1 -Path <path>` (Windows) for every affected
   route, including error cases.
7. **Reconcile any diff** the script reports until output is identical (after
   timestamp-key normalisation). Report what changed.

## Definition of done
- Target backend implements the feature across all three layers.
- Target backend tests pass.
- `compare-responses` shows identical output for every affected route.
```

## Step 3 — Add the reference note

```md
<!-- .github/skills/port-endpoint/contract-notes.md -->
# Allowed cross-backend response differences

Exactly one difference between the backends is permitted:

| Aspect | Python (FastAPI) | .NET / Java |
|--------|------------------|-------------|
| Timestamp keys | `created_at`, `updated_at` | `createdAt`, `updatedAt` |

Timestamp **format** is the same everywhere: ISO-8601, no timezone offset
(e.g. `2026-08-31T10:15:00`). The board UI does not depend on the key casing.

**Everything else must match exactly:**
- Field names and order are not significant, but the *set* of fields must be
  identical.
- Types must match (`id` is a number, `description`/`assignee` may be `null`).
- `status` is always one of `todo`, `in-progress`, `done`.
- List endpoints return the same ordering for the same query.
- Error bodies: `404` for a missing id, `422` for a missing title or unknown
  status — same shape the source backend already returns.
```

## Step 4 — Add the bundled comparison scripts

```bash
# .github/skills/port-endpoint/scripts/compare-responses.sh
#!/usr/bin/env bash
# Compare the same request against two Task Board backends.
# Usage: compare-responses.sh <path> [base-a] [base-b]
#   compare-responses.sh /api/tasks http://localhost:8000 http://localhost:5088
# Requires: curl, jq (1.6+).
set -euo pipefail
path="${1:?usage: compare-responses.sh <path> [base-a] [base-b]}"
a="${2:-http://localhost:8000}"   # Python
b="${3:-http://localhost:5088}"   # .NET  (use :8080 for Java)

norm() {
  jq -S 'walk(
    if type == "object"
    then with_entries(.key |= (sub("^created_at$";"createdAt") | sub("^updated_at$";"updatedAt")))
    else . end)'
}

if diff <(curl -fsS "$a$path" | norm) <(curl -fsS "$b$path" | norm); then
  echo "IDENTICAL (after timestamp-key normalisation): $path"
else
  echo "DIFFERENCE at $path — see the diff above" >&2
  exit 1
fi
```

```powershell
# .github/skills/port-endpoint/scripts/compare-responses.ps1
# Compare the same request against two Task Board backends.
# Usage: .\compare-responses.ps1 -Path /api/tasks [-BaseA ...] [-BaseB ...]
param(
  [Parameter(Mandatory)][string]$Path,
  [string]$BaseA = "http://localhost:8000",   # Python
  [string]$BaseB = "http://localhost:5088"    # .NET  (use :8080 for Java)
)
$ErrorActionPreference = "Stop"

function Get-Normalized([string]$url) {
  (Invoke-RestMethod -Uri $url | ConvertTo-Json -Depth 20) `
    -replace '"created_at"', '"createdAt"' `
    -replace '"updated_at"', '"updatedAt"'
}

$a = Get-Normalized "$BaseA$Path"
$b = Get-Normalized "$BaseB$Path"

if ($a -eq $b) {
  "IDENTICAL (after timestamp-key normalisation): $Path"
} else {
  Compare-Object ($a -split "`n") ($b -split "`n") | Format-Table -AutoSize
  throw "DIFFERENCE at $Path"
}
```

Make the shell script executable (macOS / Linux):

```bash
chmod +x .github/skills/port-endpoint/scripts/compare-responses.sh
```

## Step 5 — Use the skill

You need two backends from Module 01 running (e.g. Python on `:8000` and .NET on
`:5088`) plus the database.

### In the Copilot CLI (or agent mode)

```
> Port the updated_at sorting feature (GET /api/tasks?sort=-updated_at) from the
  Python backend to the .NET backend.
```

- If your Copilot build auto-discovers repo skills, it will announce that it is
  using **port-endpoint** and follow the procedure.
- If not, point it explicitly:

  ```
  > Follow .github/skills/port-endpoint/SKILL.md to port the updated_at sorting
    feature from the Python backend to the .NET backend.
  ```

Watch that it:
- reads `contract-notes.md` before matching the JSON,
- puts the `ORDER BY` in the .NET **repository**,
- adds xUnit tests mirroring the pytest cases,
- runs `compare-responses` at the end.

### Run the verification script yourself

**macOS / Linux**

```bash
.github/skills/port-endpoint/scripts/compare-responses.sh "/api/tasks?sort=-updated_at"
```

**Windows (PowerShell)**

```powershell
.\.github\skills\port-endpoint\scripts\compare-responses.ps1 -Path "/api/tasks?sort=-updated_at"
```

Expect `IDENTICAL (after timestamp-key normalisation)`. Also check an error
case:

```bash
.github/skills/port-endpoint/scripts/compare-responses.sh "/api/tasks?sort=bogus"
```

## Step 6 — Commit

```bash
git add .github/skills && git commit -m "Add port-endpoint agent skill"
```

## Challenge — build a second skill: `api-contract-check`

Create `.github/skills/api-contract-check/SKILL.md` that, given a backend,
verifies every route in `usecase.md`'s API-contract table is implemented with
the right method, path, status codes, and body shape — and reports gaps. Bundle
a `checklist.md` derived from the contract table. Trigger it with:
`Check the Java backend against the API contract.`

Keep the `description` sharp — that one line is the only thing the agent sees
when deciding whether to use it.

## Verify

- [ ] `.github/skills/port-endpoint/` contains `SKILL.md`, `contract-notes.md`,
      and both scripts.
- [ ] `SKILL.md` frontmatter has a `name` and a specific, trigger-worthy
      `description`.
- [ ] The agent follows the skill (auto or when pointed at it) and ends by
      running `compare-responses`.
- [ ] The script prints `IDENTICAL` for the ported route.
- [ ] (Challenge) `api-contract-check` exists and reports on a backend.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Agent never uses the skill | Make the `description` match how you actually phrase the task (verbs + nouns: "port", "backend", "parity"). Or invoke it by path explicitly. |
| `jq: command not found` | Install jq (`brew install jq` / `apt install jq` / `winget install jqlang.jq`); or use the PowerShell script, which needs no jq. |
| Script: `curl (7) Failed to connect` | The backend on that port isn't running. Start it per Module 01, or pass the right `base-a` / `base-b`. |
| `compare-responses` flags a real diff | That's the skill working — reconcile the target backend until output matches. |
| Skill body too long / ignored | Keep `SKILL.md` to the procedure; push detail into bundled files it references, like `contract-notes.md`. |

## Recap & carry-forward

You now have a reusable, script-bearing capability in the repo. **Lab 05** gives
Agent mode live external tools via MCP; **Lab 06** hands work to the cloud coding
agent, which reads these same skills.
