# Module 07 — MCP-Enabled Workflows & Custom MCP Server Creation (Hands-On Labs)

Companion labs for the Module 07 deck
([`presentations/Module07_MCP_Workflows_Custom_Server.pdf`](../../presentations/Module07_MCP_Workflows_Custom_Server.pdf)).
The module has two halves:

1. **Consume** approved MCP servers inside GitHub Copilot agent mode — Jira, GitHub, a browser — and see the approval and untrusted-result steps first-hand (Labs 01–03).
2. **Build** a small custom MCP server with FastMCP, test it with the MCP Inspector, wire it into Copilot and govern it (Labs 04–06).

Every lab ends with the deck's **one-page governance record** (owner, purpose, tools, data, auth, approval, off switch).

| Lab | Focus | Server | Time | You produce |
|-----|-------|--------|------|-------------|
| [01](lab-01-atlassian-rovo-mcp-jira.md) | Access and update **Jira** work items | Atlassian Rovo MCP (remote, OAuth) | ~40 min | `jira-summary.md`, `spec-from-jira.md`, `jira-governance.md` |
| [02](lab-02-github-mcp-pull-requests.md) | **Pull request** triage, drafting and review | GitHub MCP (remote, OAuth/PAT) | ~45 min | `pr-triage.md`, a draft PR, `github-mcp-governance.md` |
| [03](lab-03-playwright-mcp-e2e-tests.md) | **Automate E2E tests** with a real browser | Playwright MCP (local, stdio) | ~50 min | `tests/todo.spec.ts`, `playwright-mcp-governance.md` |
| [04](lab-04-first-fastmcp-server.md) | Your first **custom server**, tested in the Inspector | FastMCP (local, stdio) | ~30 min | `server_minimal.py`, Inspector results |
| [05](lab-05-tools-resources-prompts.md) | Tool design: typed/bounded tools, a guarded write, a resource, a prompt | FastMCP | ~40 min | `server.py`, `test-notes.md`, an extra `pytest` test |
| [06](lab-06-wire-into-copilot-and-govern.md) | Wire into Copilot, test approvals + prompt injection, govern | FastMCP (stdio + HTTP) | ~45 min | `.vscode/mcp.json`, `governance.md` |

Labs 01–03 are independent of each other; do whichever your environment allows.
Labs 04–06 are a sequence. Total: about **4 hours** for everything. The deck's
Lab 1 (*Connect and Validate*, GitHub MCP) corresponds to Lab 02 here; its Lab 2
(*Build, Wire, Govern*) to Labs 04–06. Labs 01 and 03 extend the module to Jira
and browser-based test automation.

## Folders

| Path | Used by | What |
|------|---------|------|
| [`e2e-playwright/`](e2e-playwright/) | Lab 03 | Playwright Test project, empty `tests/`, `reference/` answer key, MCP config example |
| [`custom-mcp-server/`](custom-mcp-server/) | Labs 04–06 | FastMCP server, tests, governance record, and [`TESTING.md`](custom-mcp-server/TESTING.md) — the step-by-step guide to testing with **pytest → MCP Inspector → GitHub Copilot** |

## Prerequisites

| Need | Labs |
|------|------|
| VS Code **1.101+** with GitHub Copilot, **Agent mode** | all |
| Your org's Copilot **"MCP servers in Copilot"** policy enabled (Business/Enterprise) — ask your admin | all |
| An Atlassian cloud site with Jira and a **sandbox project**; Rovo MCP allowed by your Atlassian admin | 01 |
| A GitHub **sandbox repo** you own, with a branch ahead of `main` | 02 |
| Node.js 18+ and internet access to the public TodoMVC demo | 03 (and `npx`, used for the Inspector, in 04–06) |
| [`uv`](https://docs.astral.sh/uv/) (it manages Python) | 04–06 |

## Platform conventions

Shell blocks are given for **macOS / Linux (bash/zsh)** and **Windows
(PowerShell)** wherever they differ. WSL2 users follow the macOS / Linux side.
`.vscode/` is git-ignored in this repo, so each lab ships its MCP config as
`vscode-mcp.json.example` for you to copy into your own `.vscode/mcp.json`.

## Ground rules for every lab

- **Read-only first**, add writes only with an approval step, and only in a sandbox.
- Approve each write call **once**; never "always allow" a write tool.
- **Tool results are untrusted input.** Each lab includes a small injection test.
- **No secrets in `mcp.json`** — OAuth in the browser, or `${input:…}` prompts.
- Servers and flags change quickly: where a lab says *verify against current docs*, do.

## What's next

**Module 08** uses agents and MCP tools to review pull requests, enforce quality
gates and judge AI output — the governance habits from these labs carry over.
