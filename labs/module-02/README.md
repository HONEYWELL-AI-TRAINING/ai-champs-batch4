# Module 02 — GitHub Copilot Enterprise: Advanced Features & Engineering Workflows (Hands-On Lab)

## What this lab is

Module 01 built the **Engineering Task Board** — a small full-stack app
(PostgreSQL + React board + one of a .NET / Python / Java backend behind a
shared API contract). **This module does not build a new app.** It keeps the
Module 01 codebase as the base and layers GitHub Copilot's **intermediate-to-advanced
enterprise capabilities** on top of it, as a set of guided exercises:

| Lab | Capability | GitHub feature exercised |
|-----|-----------|--------------------------|
| [01](lab-01-repository-and-path-instructions.md) | Repository & path-specific custom instructions | `.github/copilot-instructions.md`, `AGENTS.md`, `.github/instructions/*.instructions.md` |
| [02](lab-02-prompt-files.md) | Reusable prompts (team slash-commands) | `.github/prompts/*.prompt.md` |
| [03](lab-03-custom-chat-modes-and-agents.md) | Custom chat modes / custom agents | `.github/chatmodes/*.chatmode.md`, `.github/agents/*.md` |
| [04](lab-04-skills.md) | Agent skills (reusable capability packages) | `.github/skills/<name>/SKILL.md` + bundled scripts |
| [05](lab-05-agent-mode-and-mcp.md) | Agent mode + Model Context Protocol tools | `.vscode/mcp.json`, agent-mode multi-file edits |
| [06](lab-06-copilot-coding-agent.md) | Copilot coding agent on GitHub.com | Assigning issues to Copilot, `copilot-setup-steps.yml` |
| [07](lab-07-copilot-code-review.md) | Automated Copilot code review | PR review, path filters, review instructions |
| [08](lab-08-copilot-cli-and-actions.md) | Copilot CLI + Actions authoring | `copilot` / `gh copilot`, workflow generation |

Work through them in order — each builds a customization file that later labs
reuse. Total time: about **2.5 hours**.

> **This is still the same codebase you keep evolving.** Every file you add
> here (`.github/`, `.vscode/mcp.json`) travels with the repository into
> Module 03 and beyond.

## Prerequisites

- **Module 01 completed** — the Task Board runs locally (database + one backend
  + frontend), and its tests pass. See [`labs/module-01/README.md`](../module-01/README.md).
- [Module 01 prerequisites](../setup/prerequisites.md) — Git, Node, your chosen
  backend toolchain.
- **GitHub Copilot Enterprise** (or Business) enabled for your account, and you
  are signed in to GitHub inside your IDE.
- **VS Code** with the *GitHub Copilot* and *GitHub Copilot Chat* extensions
  (latest version). JetBrains and Visual Studio have most of the same features
  under slightly different menus — notes are inline where they differ.
- **GitHub CLI** (`gh`) — [cli.github.com](https://cli.github.com). Check with
  `gh --version`; sign in with `gh auth login`.
- A GitHub repository you can push this project to (labs 05–07 need one). A
  private repo under your team or a personal fork is fine.

## Platform conventions

Command blocks are given for **macOS / Linux (bash/zsh)** and **Windows
(PowerShell)**. Run the pair that matches your machine. WSL2 users follow the
macOS / Linux side. Actions taken *inside the editor* (opening Copilot Chat,
switching modes, accepting a diff) are the same on every OS.

## Set-up — do this once before Lab 01

### 1. Open the Task Board as the workspace root

Copilot reads customization files **relative to the folder you open as your
workspace/project root**. Open `labs/module-01/` directly:

**macOS / Linux**

```bash
cd labs/module-01
code .            # or: open this folder in JetBrains / Visual Studio
```

**Windows (PowerShell)**

```powershell
cd labs\module-01
code .
```

Every path in these labs (e.g. `.github/copilot-instructions.md`) is therefore
**inside `labs/module-01/`**.

### 2. Create a working branch

Keep all Module 02 additions isolated and reviewable:

```bash
git checkout -b module-02-copilot
```

(Same command on every OS.)

### 3. Confirm Copilot is live

Open Copilot Chat (VS Code: the chat icon in the Activity Bar, or
`Ctrl`/`Cmd`+`Alt`+`I`) and ask: `What workspace am I connected to?`
You should get a response that references the Task Board files. If Copilot says
you are not signed in or not licensed, resolve that with your GitHub admin
before continuing.

### 4. Verify the base app still works

**macOS / Linux**

```bash
# from labs/module-01/ — pick the backend you used in Module 01
cd backend-python && pytest        # or: cd backend-dotnet && dotnet test
cd ../frontend && npm test -- --run
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest         # or: cd backend-dotnet ; dotnet test
cd ..\frontend ; npm test -- --run
```

Green tests are your safety net: every lab below asks you to re-run them after
Copilot makes a change.

## How each lab is structured

1. **Objective** — the one capability you will be able to use afterwards.
2. **Why it matters for the enterprise** — the governance / consistency reason.
3. **Steps** — numbered, copy-paste-able, both platforms.
4. **Files to create** — full content, ready to paste (the path is the first
   line of every code block).
5. **Verify** — how to prove it worked.
6. **Recap & carry-forward** — what the next lab reuses.

## A note on Copilot's pace of change

GitHub ships Copilot changes almost weekly. File formats and menu locations in
these labs are current as of the course date; if a path or setting name has
moved, the [Module 02 guide](../../guides/module-02-copilot-enterprise.md) and
the official docs linked there are the source of truth. The *concepts* —
repository-scoped instructions, reusable prompts, scoped agents, skills, MCP
tools — are stable.

## After this module

- The Task Board repo now carries a full Copilot customization layer.
- [Module 03](../module-03/README.md) uses these instruction and prompt files
  as the basis for context engineering.
- [Module 04](../module-04/index.html) builds the next feature spec-first on the
  same repo, reusing the custom chat modes (Lab 03) and skills (Lab 04) you
  create here.
