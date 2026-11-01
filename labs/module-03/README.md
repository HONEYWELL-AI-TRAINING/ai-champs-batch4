# Module 03 — Context Engineering (Hands-On Lab)

## What this lab is

Module 03 does not build a new app. It keeps the **Engineering Task Board** from
Module 01 as the base and the Copilot customization layer from Module 02
(`.github/copilot-instructions.md`, prompt files, chat modes, skills) as the
starting point. On top of that it teaches the discipline every later module
depends on: **engineering the context** you feed the model — selecting,
compressing, and scoping it — so quality goes up and token cost stays flat.

| Lab | Focus | You produce |
|-----|-------|-------------|
| [01](lab-01-prompt-only-vs-context-engineered.md) | Prompt-only vs context-engineered, measured | A filled [token worksheet](token-worksheet.md) comparing both passes |
| [02](lab-02-select-compress-scope.md) | Select → compress → scope, and bottle it | `worksheets/context-manifest.md`, `.github/prompts/context-brief.prompt.md`, `CONTEXT.md` |

Work through them in order. Total time: about **75 minutes**.

## The shared task for Module 03

Every lab works the **same feature** so you can compare approaches cleanly:

> **Add `GET /api/tasks/stats`** to your chosen backend. It returns the number of
> tasks in each status, plus a total:
>
> ```json
> { "todo": 3, "in-progress": 2, "done": 1, "total": 6 }
> ```
>
> Rules (the same ones a context-engineered prompt will supply, and a
> prompt-only one usually misses):
> - The three status keys are **exactly** `todo`, `in-progress`, `done` — the
>   literal `status` values, hyphen and all. Not `inProgress`.
> - The count/aggregation query lives in the **repository** layer.
> - No change to `database/schema.sql`.
> - A test is added in the matching test file before the work is "done".
> - The other two backends would return byte-identical JSON for the same call.

You implement it for real in Lab 01 and refine the *approach* in Lab 02.

## Prerequisites

- **Modules 01 and 02 completed.** The Task Board runs locally; the
  `.github/copilot-instructions.md`, `.github/prompts/`, `.github/chatmodes/`,
  and `.github/skills/` from Module 02 are on your branch.
- [Module 01 prerequisites](../setup/prerequisites.md) and a working backend +
  frontend + database.
- **GitHub Copilot**, signed in inside VS Code. (The optional shared Copilot
  Space in Lab 02 needs Enterprise or Business; the lab works without it.)
- **VS Code** with the GitHub Copilot + Copilot Chat extensions (latest).
- `node` / `npx` on PATH (the token-estimate helper uses it).

## Platform conventions

Command blocks are given for **macOS / Linux (bash/zsh)** and **Windows
(PowerShell)**. WSL2 users follow the macOS / Linux side. Editor actions
(opening chat, adding context with `#`, switching modes) are identical on every
OS.

## Set-up — do this once before Lab 01

### 1. Open the Task Board as the workspace root

**macOS / Linux**

```bash
cd labs/module-01
code .
```

**Windows (PowerShell)**

```powershell
cd labs\module-01
code .
```

All paths in these labs (`.github/…`, `worksheets/…`) are **inside
`labs/module-01/`**.

### 2. Branch from your Module 02 work

```bash
git checkout module-02-copilot     # or wherever Module 02 landed
git checkout -b module-03-context
```

Confirm the Module 02 layer is present:

**macOS / Linux**

```bash
ls .github/copilot-instructions.md .github/prompts .github/skills
```

**Windows (PowerShell)**

```powershell
Get-ChildItem .github\copilot-instructions.md, .github\prompts, .github\skills
```

If it's missing, complete [Module 02](../module-02/README.md) first — these labs
build directly on it.

### 3. Create the worksheets folder and token helper

**macOS / Linux**

```bash
mkdir -p worksheets tools
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force -Path worksheets, tools | Out-Null
```

Add a rough token estimator (character-count ÷ 4 — good enough for *comparing*
two contexts; the IDE shows exact numbers where it can):

```bash
# tools/estimate-tokens.sh
#!/usr/bin/env bash
# Rough token estimate for one or more files (or stdin). ~4 chars/token.
# Usage: tools/estimate-tokens.sh file1 [file2 ...]   |   cat x | tools/estimate-tokens.sh
set -euo pipefail
total=0
if [ "$#" -eq 0 ]; then
  chars=$(wc -c | tr -d ' '); echo "stdin: ~$((chars / 4)) tokens ($chars chars)"; exit 0
fi
for f in "$@"; do
  chars=$(wc -c < "$f" | tr -d ' ')
  printf '%-45s ~%6d tokens  (%d chars)\n' "$f" "$((chars / 4))" "$chars"
  total=$((total + chars))
done
printf '%-45s ~%6d tokens  (%d chars)\n' "TOTAL" "$((total / 4))" "$total"
```

```powershell
# tools/estimate-tokens.ps1
# Rough token estimate (~4 chars/token) for comparing contexts.
# Usage: .\tools\estimate-tokens.ps1 file1 [file2 ...]
param([Parameter(ValueFromRemainingArguments)][string[]]$Paths)
$total = 0
foreach ($p in $Paths) {
  $chars = (Get-Content -Raw -LiteralPath $p).Length
  "{0,-45} ~{1,6} tokens  ({2} chars)" -f $p, [int]($chars / 4), $chars
  $total += $chars
}
"{0,-45} ~{1,6} tokens  ({2} chars)" -f "TOTAL", [int]($total / 4), $total
```

Make it executable (macOS / Linux):

```bash
chmod +x tools/estimate-tokens.sh
```

> **For exact counts** (optional): `npx @anthropic-ai/tokenizer <file>` or an
> equivalent tiktoken CLI. Copilot Chat in current VS Code also shows a context
> gauge on the chat input — hover it for the token figure.

### 4. Commit the scaffolding

```bash
git add tools && git commit -m "Module 03: token estimation helper"
```

## How each lab is structured

Objective → Why it matters for the enterprise → Background → Steps (both
platforms) → Files/templates → Verify → Troubleshooting → Recap & carry-forward.

## A note on Copilot's pace of change

Context controls (`#`-mentions, the Add Context button), Copilot Spaces, and the
model picker move often. Menu names in these labs are current as of the course
date; the [Module 03 guide](../../guides/module-03-prompt-context-engineering.md)
links the authoritative docs. The *concepts* — select → compress → scope,
context boundaries — are stable.

## After this module

- The repo carries a reusable `/context-brief` prompt and a `CONTEXT.md`.
- You have a measured baseline (the token worksheet) for later cost discussions.
- [Module 04](../module-04/README.md) writes specifications on top of exactly
  this context discipline — a spec is only as precise as the context behind it.
