# Lab 05 — Agent Mode + Model Context Protocol (MCP) Tools

**Time:** ~25 min · **Surface:** VS Code Agent mode ·
**Prereq:** Lab 04 complete; the Task Board database running (from Module 01)

## Objective

Use **Agent mode** to make a real multi-file change to the Task Board — add
`GET /api/tasks?sort=-updated_at` sorting across router, service, repository, UI,
and tests in one reviewed pass. Then wire an **MCP server** into the workspace so
the agent can use an external tool (filesystem, GitHub, or a Postgres inspector)
as part of its reasoning.

## Why it matters for the enterprise

Agent mode is the same repository-aware reasoning that Module 05 (brownfield) and
Module 07 (MCP-enabled agents) build on. Doing a governed agent change now — with
a reviewed diff and green tests — sets the habit. MCP is how you give that agent
**controlled** access to systems beyond the code (a ticketing system, a schema
registry, a design system) without pasting their contents into chat.

## Background

- **Agent mode** plans, edits multiple files, runs terminal commands (with your
  approval), reads test output, and iterates. You review one combined diff.
- **MCP** is an open protocol for exposing tools to an AI client. VS Code reads
  MCP server definitions from **`.vscode/mcp.json`** in the workspace.
- Each MCP tool call in agent mode asks for approval the first time. Enterprise
  policy may restrict which servers are allowed — check with your admin before
  adding one that reaches outside the repo.

---

## Part A — A governed agent-mode change

### Step 1 — Start from a clean tree

```bash
git status          # should be clean; commit or stash anything outstanding
```

Make sure the database and your backend run (Module 01 steps). Agent mode will
want to run the test suite.

### Step 2 — Switch to Agent mode and brief it

In Copilot Chat, select **Agent** from the mode dropdown. Send:

```
Implement sorting for the task list in the CURRENTLY OPEN backend.

- GET /api/tasks?sort=-updated_at  → newest-updated first
- GET /api/tasks?sort=updated_at   → oldest-updated first
- No sort param → unchanged (id ascending)
- Unknown sort value → 422, consistent with the existing error contract

Follow .github/copilot-instructions.md: the ORDER BY belongs in the repository
query, not the controller. Add/adjust tests first. Then add a matching control
in the React task list (frontend/src/) that calls the sorted endpoint through
the services layer.

Run the backend tests and the frontend tests. Show me the full diff. Do not
change database/schema.sql.
```

### Step 3 — Supervise it

- **Approve terminal commands** it proposes one at a time; read each before
  approving. Deny anything that isn't a build/test/git-status command.
- When it pauses on a failing test, let it iterate — but read the fix.
- If it edits `database/schema.sql` or adds a migration, **reject that hunk** and
  tell it the schema is fixed.

### Step 4 — Review the combined diff

Open the Source Control view. Check, against the concept guide's
*Model / Task Selection & Safe Enterprise Usage*:

- [ ] `ORDER BY` / `.order_by()` / `OrderBy(...)` is in the **repository** only.
- [ ] The `422` for an unknown sort value uses the **existing** error path.
- [ ] New tests cover: `-updated_at`, `updated_at`, no param, bad param.
- [ ] The frontend calls the endpoint through `src/services/`, not `fetch` in a
      component.
- [ ] No change to `schema.sql`.

Run the suites yourself:

**macOS / Linux**

```bash
cd backend-python && pytest -q            # or dotnet test / ./mvnw -B test
cd ../frontend && npm test -- --run
```

**Windows (PowerShell)**

```powershell
cd backend-python ; pytest -q
cd ..\frontend ; npm test -- --run
```

### Step 5 — Commit (or discard and retry the prompt)

```bash
git add -A && git commit -m "Add updated_at sorting to task list (agent mode)"
```

> **Compare with Module 01 Exercise 2.** You did this same feature by hand there.
> Note the wall-clock difference *and* the review effort — the point of the
> module is knowing which is worth it for which change.

---

## Part B — Add an MCP server

### Step 6 — Create `.vscode/mcp.json`

**macOS / Linux**

```bash
mkdir -p .vscode
```

**Windows (PowerShell)**

```powershell
New-Item -ItemType Directory -Force -Path .vscode | Out-Null
```

Start with the **filesystem** server — safe, local, no credentials — scoped to
this project:

```jsonc
// .vscode/mcp.json
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
    }
  }
}
```

### Step 7 — (Optional) add the GitHub MCP server

Only if your org permits it. This one needs a token — VS Code will prompt and
store it securely; do **not** hard-code it.

```jsonc
// .vscode/mcp.json  — add alongside "filesystem"
{
  "servers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:github_token}" }
    }
  },
  "inputs": [
    {
      "id": "github_token",
      "type": "promptString",
      "description": "GitHub PAT (repo scope) for the MCP GitHub server",
      "password": true
    }
  ]
}
```

### Step 8 — Start the server and use a tool

1. Open `.vscode/mcp.json`. VS Code shows a **Start** code-lens above each
   server — click it. Check the **MCP: List Servers** command (Command Palette)
   shows it *Running*.
2. In Agent mode, click the **Tools** icon in the chat input and confirm the
   MCP tools appear (they are toggled on per chat).
3. Ask something that needs the tool:

   ```
   Using the filesystem tools, list every file under frontend/src/services/ and
   summarise what each one is responsible for. Then tell me whether the new
   sort control added in Part A put its HTTP call in the right place.
   ```

4. Approve the tool call when prompted. The agent should read the real files via
   MCP rather than guessing.

### Step 9 — Commit the config

```bash
git add .vscode/mcp.json && git commit -m "Add MCP server config (filesystem)"
```

> `.vscode/mcp.json` holds **no secrets** — tokens go through `inputs` prompts
> and VS Code's secret storage. Confirm `git diff` shows no token before you
> commit.

## Verify

- [ ] The sort feature is implemented, tests are green, `schema.sql` untouched.
- [ ] `git log` shows a single reviewed commit for the agent change.
- [ ] `.vscode/mcp.json` exists; **MCP: List Servers** shows `filesystem`
      running.
- [ ] An agent-mode request successfully calls an MCP tool after your approval.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Agent won't run tests | Approve the terminal command when prompted; check *Chat › Agent: terminal auto-approve* settings aren't blocking everything. |
| Agent keeps editing schema | Reject the hunk, restate the rule; consider running the *API Reviewer* mode on the result. |
| MCP server won't start | You need Node/`npx` on PATH. Run `npx -y @modelcontextprotocol/server-filesystem --help` in a terminal to see the real error. |
| GitHub MCP 401 | The PAT lacks scope or expired. Re-run the input prompt (Command Palette → **MCP: Reset Cached Tokens** or restart the server). |
| Tools don't show in chat | Click the Tools icon in the chat input and enable them for this session. |

## Recap & carry-forward

You have run a governed multi-file agent change and given the agent an external
tool. **Lab 06** moves the same kind of work to GitHub.com, where the Copilot
coding agent does it asynchronously and opens a PR.
