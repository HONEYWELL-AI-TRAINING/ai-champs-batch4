# GitHub Spec Kit Setup

[GitHub Spec Kit](https://github.com/github/spec-kit) is the toolkit that drives
**spec-driven development** from Module 04 on. It gives you:

- a `specify` **CLI** that scaffolds the artifact set into a repo, and
- a set of **slash commands** (`/speckit.constitution`, `/speckit.specify`,
  `/speckit.clarify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.analyze`,
  `/speckit.implement`, `/speckit.checklist`) that run inside your AI coding
  agent.

You install the CLI **once per machine**. You run `specify init` **once per
repo** (for these labs, inside `labs/module-01/`).

Commands are shown for **macOS / Linux (bash/zsh)** and **Windows
(PowerShell)** — run the pair that matches your machine. WSL2 users follow the
macOS / Linux side inside their Linux distribution.

---

## Prerequisites

| Tool | Version | Check | Notes |
|------|---------|-------|-------|
| Git | 2.40+ | `git --version` | Spec Kit creates a feature branch per spec |
| Python | 3.11+ | `python3 --version` (Windows: `python --version`) | the `specify` CLI is a Python tool |
| `uv` | latest | `uv --version` | Astral's Python package/tool manager — installs and runs `specify` |
| An AI coding agent | — | — | GitHub Copilot in VS Code for this programme; Claude Code, Gemini CLI, Cursor and others are also supported |
| Internet access | — | — | `specify init` fetches templates from GitHub (offline fallback below) |

> `pipx` works instead of `uv` if you already have it. Everywhere this guide
> says `uv tool install …`, the `pipx install …` equivalent is noted.

---

## Step 1 — Install `uv`

Skip if `uv --version` already prints a version.

**macOS / Linux**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

or with Homebrew: `brew install uv`

**Windows (PowerShell)**

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

or with winget: `winget install --id=astral-sh.uv -e`

**Close and reopen your terminal** so `PATH` picks up `uv`, then confirm:

```
uv --version
```

---

## Step 2 — Install the `specify` CLI

### Option A — Persistent install (recommended)

Installs `specify` as a global tool you can call from any directory.

```
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

<sub>pipx equivalent: `pipx install git+https://github.com/github/spec-kit.git`</sub>

Reopen the terminal, then verify:

```
specify --version
specify check
```

`specify check` reports which AI agents and script tools it can find on your
machine. It is fine for some to be missing — you only need the agent you use.

### Option B — Run without installing

If you would rather not install anything globally, prefix every command with
`uvx`. Use the **same** form each time so the labs' `specify init …` lines still
work:

```
uvx --from git+https://github.com/github/spec-kit.git specify init --here --integration copilot --script sh
```

---

## Step 3 — Initialise Spec Kit in the repo

For these labs the workspace root is `labs/module-01/`.

**macOS / Linux**

```bash
cd labs/module-01
specify init --here --integration copilot --script sh
```

**Windows (PowerShell)**

```powershell
cd labs\module-01
specify init --here --integration copilot --script ps
```

To scaffold a **brand-new** project instead of an existing folder, replace
`--here` with a name: `specify init my-project --integration copilot --script sh`.

### Flags that matter

| Flag | Purpose |
|------|---------|
| `--here` | Initialise in the current directory (no subfolder). Prompts if it is not empty. |
| `--force` | Proceed in a non-empty directory without prompting. It **merges** — it adds `.specify/` and the agent's prompt files, and does not overwrite your source. Commit your work first so you can inspect the diff. |
| `--ai <agent>` | Which agent's slash-command files to generate — see table below. |
| `--script <sh\|ps>` | Helper-script flavour: **`sh`** on macOS / Linux / WSL, **`ps`** on native Windows PowerShell. |
| `--no-git` | Skip git branch/commit automation. |
| `--ignore-agent-tools` | Don't fail if the chosen agent's CLI isn't installed (fine for Copilot-in-VS-Code). |

Common `--ai` values: `copilot`, `claude`, `gemini`, `cursor`, `codex`,
`windsurf`, `qwen`, `opencode`. Run `specify init --help` for the current full
list.

---

## Step 4 — Confirm the scaffold

After `init` you should have (inside `labs/module-01/`):

```
.specify/
├── memory/                     # constitution.md lands here (Lab 01)
├── scripts/                    # sh/ or ps/ helper scripts
└── templates/                  # spec / plan / tasks templates
.github/
└── prompts/
    └── speckit.*.prompt.md     # one per slash command  (Copilot)
```

The prompt-file location depends on `--ai`:

| Agent | Slash-command files |
|-------|---------------------|
| `copilot` | `.github/prompts/speckit.*.prompt.md` |
| `claude` | `.claude/commands/speckit.*.md` |
| `gemini` | `.gemini/commands/speckit.*.toml` |
| `cursor` | `.cursor/commands/speckit.*.md` |

Commit the scaffold:

```bash
git add .specify .github && git commit -m "Initialise Spec Kit"
```

---

## Step 5 — Verify the slash commands load

1. Open the repo in your agent (VS Code for Copilot: `code .` from
   `labs/module-01/`). **Reload the window** if it was already open.
2. Open the chat panel and type `/speckit.` — the seven commands should
   autocomplete.
3. Older Spec Kit installs use bare names (`/constitution`, `/specify`,
   `/plan`, …). If `/speckit.*` doesn't appear but the bare names do, that is
   fine — use those.

You are ready for **[Module 04 · Lab 01](../module-04/lab-01-constitution-and-spec.md)**.

---

## Updating and uninstalling

| Action | Command |
|--------|---------|
| Update the CLI | `uv tool upgrade specify-cli` (pipx: `pipx upgrade specify-cli`) |
| Refresh templates in a repo | re-run `specify init --here --force --ai … --script …`, then review the diff |
| Uninstall the CLI | `uv tool uninstall specify-cli` (pipx: `pipx uninstall specify-cli`) |

---

## Offline / air-gapped fallback

If `specify init` cannot reach GitHub:

1. On a machine with access: `git clone https://github.com/github/spec-kit.git`.
2. Copy `spec-kit/templates/` and `spec-kit/scripts/` into your repo's
   `.specify/` folder.
3. Copy the command prompt files from `spec-kit/.github/prompts/` (or the
   agent-specific folder) into your repo.
4. Create `.specify/memory/constitution.md` by hand from
   `templates/constitution-template.md`.

The slash commands are just prompt files — once they are in place, the workflow
runs without the CLI.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `specify: command not found` / `not recognized` | Reopen the terminal so `PATH` updates. Still failing: `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` (or use Option B's `uvx …` form). |
| `uv: command not found` after install | The installer prints a line to add to your shell profile — run it, or reopen the terminal. On Windows, check `%USERPROFILE%\.local\bin` is on `PATH`. |
| `specify init` fails to download templates | Network/proxy/firewall blocking GitHub. Use the offline fallback above. |
| `init` refuses — "directory is not empty" | Pass `--force`. It merges; it does not wipe. Commit first to see its diff. |
| Slash commands don't appear in chat | Reload the IDE window. Confirm the prompt files exist (`.github/prompts/speckit.*.prompt.md` for Copilot). Older installs: use `/specify`, not `/speckit.specify`. |
| `specify check` shows your agent as missing | Only blocks if you rely on that agent's CLI. For Copilot-in-VS-Code, add `--ignore-agent-tools` to `init`. |
| Python version error | `specify` needs Python 3.11+. `uv` can supply one: `uv python install 3.12`. |
| PowerShell blocks a script with an execution-policy error | Run once: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, then retry. |

---

## See also

- [Lab prerequisites](prerequisites.md) — the full course toolchain
- [Module 04 — Spec-Driven Development](../module-04/README.md) — the first module that uses Spec Kit
- [github/spec-kit](https://github.com/github/spec-kit) · [Spec Kit docs](https://github.github.com/spec-kit/)
- [docs.astral.sh/uv](https://docs.astral.sh/uv/) — the `uv` toolchain
