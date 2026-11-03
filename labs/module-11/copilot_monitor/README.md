# Copilot Practice Lab

Local web app that measures how a Copilot practice (scoped prompt, attached file, repo instructions) changes
**tokens per task**, **prompts per task**, LLM/tool calls, time and answer quality.
Source: Copilot Chat's OpenTelemetry export → `server.py` → browser.

Verified on Linux with Python 3.12. Windows/macOS commands are the standard equivalents and were **not** run.

## Requirements

| Item | Minimum | Check |
|---|---|---|
| Python | 3.10 (tested 3.12) | `python3 --version` · Windows: `py --version` |
| pip | bundled with Python | `python3 -m pip --version` · Windows: `py -m pip --version` |
| Git | any | `git --version` |
| VS Code + GitHub Copilot Chat (signed in) | recent | Extensions view |
| OpenRouter API key | optional (LLM judge only) | https://openrouter.ai/keys |

Install Python if missing or < 3.10, then reopen the terminal:

| OS | Command |
|---|---|
| Windows | installer from https://www.python.org/downloads/ (tick **Add python.exe to PATH**), or `winget install Python.Python.3.12` |
| macOS | `brew install python@3.12` |
| Ubuntu/Debian | `sudo apt update && sudo apt install -y python3 python3-pip python3-venv` |
| Fedora | `sudo dnf install -y python3 python3-pip` |

Windows: use `py` wherever this guide says `python3`.

## Setup

Run all commands from `examples/copilot_monitor`.

**1. Get the code**
```bash
git clone https://github.com/Bosch-training/github-copilot-deep-dive.git
cd github-copilot-deep-dive
git checkout copilot-token-monitor   # skip once merged to main
cd examples/copilot_monitor
```

**2. Create the virtual environment** (once)

| OS | Command |
|---|---|
| macOS/Linux | `python3 -m venv .venv` |
| Windows | `py -m venv .venv` |

Ubuntu/Debian error `ensurepip is not available` → `sudo apt install python3-venv`, rerun.

**3. Activate it** (every new terminal)

| Shell | Command |
|---|---|
| macOS/Linux | `source .venv/bin/activate` |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows cmd | `.venv\Scripts\activate.bat` |

Prompt must start with `(.venv)`. PowerShell "scripts disabled" → `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`, rerun.

**4. Install packages**
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -c "import fastapi, uvicorn, dotenv, opentelemetry.proto; print('ok')"
```
Last command must print `ok`.

**5. Judge (optional)**

*Without judge:* skip this step. Quality column = your star ratings. To force off even with a key: `JUDGE_ENABLED=false` in `.env`.

*With judge:*

| OS | Command |
|---|---|
| macOS/Linux | `cp .env.example .env` |
| Windows PowerShell | `Copy-Item .env.example .env` |
| Windows cmd | `copy .env.example .env` |

Edit `.env`:
```
JUDGE_ENABLED=true
OPENROUTER_API_KEY=<your key>
JUDGE_MODEL=openai/gpt-4o-mini
```
- `JUDGE_MODEL`: use a different model family than the Copilot models you compare.
- `.env` is git-ignored. Never commit or paste the key.
- Prompt + answer text are sent to OpenRouter.

**6. Start the server**
```bash
python -m uvicorn server:app --port 4318
```
- Expect `Uvicorn running on http://127.0.0.1:4318`. Keep the terminal open. Stop: `Ctrl+C`.
- Open http://localhost:4318. Header shows `● live · judge: <model>` or `judge: off`.
- `address already in use` → stop the other process, or use another port here and in step 7.
- Restart after any `.env` change.

**7. Configure VS Code**

`Ctrl+Shift+P` (macOS `Cmd+Shift+P`) → **Preferences: Open User Settings (JSON)**. Add inside the top-level `{}`:
```json
"github.copilot.chat.otel.enabled": true,
"github.copilot.chat.otel.exporterType": "otlp-http",
"github.copilot.chat.otel.otlpEndpoint": "http://localhost:4318",
"github.copilot.chat.otel.captureContent": true
```
Then `Ctrl+Shift+P` → **Developer: Reload Window**.

- `captureContent` is required for prompt text and the judge.
- Settings not found → update VS Code and the Copilot Chat extension; search `otel` in Settings.
- Reference: https://code.visualstudio.com/docs/agents/guides/monitoring-agents

**8. Verify the connection**

Send any Copilot Chat message. Server terminal must show `POST /v1/traces ... 200 OK`. Row appears in the page after Copilot finishes answering.

## Measure a practice

1. Enter **Condition** (practice under test, e.g. `vague-prompt`) and **Task** (e.g. `add-modulo`) → **Start new run**. Status shows `● Recording`.
2. New Copilot chat, same model and mode every run. Do the task.
3. **Stop run**. Optional: rate the answer with stars.
4. Repeat. **≥ 3 runs per condition** (fewer shows ⚠). First condition = baseline.
5. Read **Before / after**. **Export CSV** before restarting the server (data is in memory only).

Protocols for three practices: [EXPERIMENTS.md](EXPERIMENTS.md).

## Columns

| Column | Meaning |
|---|---|
| Tokens / run | input + output over all LLM calls in the run |
| Prompts / run | prompts you sent (follow-ups = iterations) |
| LLM / tool calls | agent steps before the answer |
| Cached in / run | cached input tokens |
| AIU / run | `copilot_usage_nano_aiu` ÷ 1e9, cost proxy, unit unverified |
| Judge / Your rating | quality 1-5; higher is better, all other columns lower is better |

Prompts outside a run, and Copilot's small background calls, are not counted.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `python3`/`py` not found | Install Python (Requirements), reopen terminal |
| Any error on start before the server prints `Uvicorn running` | Check `python --version` inside the venv is ≥ 3.10. If not: install newer, delete `.venv`, redo steps 2-4 |
| `No module named fastapi`/`uvicorn` | Activate venv (step 3), reinstall (step 4) |
| Page shows `disconnected` | Server not running → step 6 |
| No `POST /v1/traces` in terminal | Recheck step 7 settings, reload window, match port |
| Rows show run `–` / missing from table | No active run; press **Start new run** first |
| Judge `HTTPError: 401` | Wrong/missing `OPENROUTER_API_KEY` |
| Judge `HTTPError: 404`/model error | Invalid `JUDGE_MODEL`; copy id from https://openrouter.ai/models |
| Model absent from results | Not instrumented by Copilot; check **Developer: Show Chat Debug View** |

## Test without Copilot

Server running, then (macOS/Linux/Git Bash):
```bash
curl -X POST localhost:4318/config -H 'content-type: application/json' -d '{"condition":"demo","task":"t"}'
curl -X POST localhost:4318/demo -H 'content-type: application/json' \
     -d '{"model":"demo","prompt":"hello","input_tokens":1200,"output_tokens":300}'
```
Windows PowerShell:
```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:4318/config -ContentType 'application/json' -Body '{"condition":"demo","task":"t"}'
Invoke-RestMethod -Method Post -Uri http://localhost:4318/demo -ContentType 'application/json' -Body '{"model":"demo","prompt":"hello","input_tokens":1200,"output_tokens":300}'
```
One row appears with condition `demo`, 1,500 tokens.

## Files

| File | Purpose |
|---|---|
| `server.py` | OTLP receiver, per-prompt grouping, run labels, optional judge |
| `index.html` | UI |
| `requirements.txt` | Python packages |
| `.env.example` | optional settings template |
| `EXPERIMENTS.md` | protocols for three practices |

## Security

- No authentication; binds to `127.0.0.1`. Do not expose port 4318.
- Data in memory only.
