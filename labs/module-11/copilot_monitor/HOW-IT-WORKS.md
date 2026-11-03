# How Copilot Practice Lab Works

This is a **measurement tool** that tracks GitHub Copilot Chat performance across different coding practices. It measures tokens, prompts, quality, and time to help you decide if a practice (like scoped prompts or file attachments) actually improves your workflow.

---

## Architecture: Three Pieces

```
VS Code (Copilot Chat)
    ↓ sends OpenTelemetry traces (OTLP/HTTP)
Python server (FastAPI) on localhost:4318
    ↓ parses & aggregates
Browser dashboard (index.html)
    ↓ displays results & SSE stream
User rates answers & exports CSV
```

---

## How a Copilot Interaction Gets Tracked

### 1. You send a message in Copilot Chat

Copilot exports OpenTelemetry data (not regular logs) to your server at `/v1/traces`. This requires VS Code settings:

```json
"github.copilot.chat.otel.enabled": true,
"github.copilot.chat.otel.otlpEndpoint": "http://localhost:4318",
"github.copilot.chat.otel.captureContent": true
```

The `captureContent` setting is **required** to capture prompt and answer text for the judge and dashboard.

### 2. Server receives raw spans

Each Copilot response is one **trace** with multiple **spans** (nested events):

- **`invoke_agent`** (root): the full request → answer cycle
  - Contains overall metadata: model, duration, final output
- **`chat`** (children): individual LLM API calls
  - Contains: input tokens, output tokens, model name, cached input tokens
- **`execute_tool`** (children): tools Copilot called
  - Examples: `read_file`, `semantic_search`, `list_directory`

### 3. Server groups & totals in `apply_span()`

The server's `apply_span()` function processes each incoming span:

```python
for span in incoming_spans:
    if name == "chat":
        rec["llm_calls"] += 1
        rec["input_tokens"] += span.tokens_in
        rec["output_tokens"] += span.tokens_out
        rec["cache_read"] += span.cache_read_tokens
        rec["aiu"] += span.copilot_usage_nano_aiu
        
    elif name == "execute_tool":
        rec["tools"].append(tool_name)
        
    elif name == "invoke_agent" and is_root:
        rec["done"] = True
        rec["model"] = extracted_model
        rec["agent"] = extracted_agent_name
        rec["duration_ms"] = end_time - start_time
        
        # Label with active condition/task/run based on timestamp
        rec.update(label_for(start_time))
```

Key insight: spans are idempotent (tracked by `spanId` in `seen_spans` set), so duplicate exports don't double-count.

### 4. Optional: judge the quality

If configured, the server sends the prompt + answer to an external LLM for **automated quality scoring**:

- **Correctness** (1–5): is the answer factually/technically right?
- **Instruction following** (1–5): does it obey every explicit constraint?

Configuration (in `.env`):
```
JUDGE_ENABLED=true
OPENROUTER_API_KEY=<your-key>
JUDGE_MODEL=openai/gpt-4o-mini
```

The judge runs **async** in a background task, so it doesn't block the dashboard. If disabled or no API key is set, the dashboard shows only your manual star ratings.

### 5. Broadcast to browser

The server stores each record in memory:

```python
traces[trace_id] = {
    "id": trace_id,
    "condition": "scoped-prompt",
    "task": "add-modulo",
    "run": 1,
    "model": "claude-3.5-sonnet",
    "input_tokens": 1200,
    "output_tokens": 350,
    "llm_calls": 2,
    "tools": ["read_file", "semantic_search"],
    "cache_read": 0,
    "aiu": 0.00042,
    "duration_ms": 4200,
    "prompt": "In examples/calculator.py add modulo...",
    "answer": "def modulo(a: float, b: float) -> float:\n    if b == 0:\n        raise ValueError(...)",
    "judge": {"correctness": 5, "instruction_following": 5, "reason": "Perfect implementation"},
    "rating": 5,  # user stars
    "done": True
}
```

Every connected browser receives updates via **Server-Sent Events** (SSE) at `/stream`:

```python
async def stream():
    q: asyncio.Queue = asyncio.Queue()
    listeners.add(q)
    
    async def gen():
        try:
            # Replay all existing records
            for rec in list(traces.values()):
                yield f"data: {json.dumps(rec)}\n\n"
            
            # Stream new records as they arrive
            while True:
                yield f"data: {json.dumps(await q.get())}\n\n"
        finally:
            listeners.discard(q)
    
    return StreamingResponse(gen(), media_type="text/event-stream")
```

The browser subscribes once and receives:
1. Historical records (instant replay)
2. Live updates as new traces complete

---

## The Experiment Workflow

### What you do:

1. **Set condition + task**  
   Example: Condition = `scoped-prompt`, Task = `add-modulo`
   - Press **Start new run**
   - Server appends a timestamped label to `labels[]`
   - Global `run_counter` increments (1, 2, 3, ...)
   - All future prompts will be tagged with this condition/task/run until stopped

2. **Open a fresh Copilot chat** and do the task
   - Every message you send and answer you receive is counted
   - If Copilot's first answer is incomplete, you send a follow-up
   - That follow-up counts as a separate **prompt** (iteration)
   - The metric "Prompts / run" = how many times you hit send

3. **Stop the run** when done
   - Press **Stop run** (optional but recommended)
   - Server appends a label with `run: 0` to disable counting

4. **Rate the final answer** (optional)
   - Click the stars to give 1–5 rating
   - Saved in the record; exported to CSV

5. **Repeat** ≥ 3 times per condition
   - First condition = baseline for comparison
   - Other conditions show % change vs. baseline
   - Minimum 3 runs per condition; fewer triggers ⚠ warning

6. **View results**
   - **Before / after** table shows averages per condition
   - Metrics: Tokens / run, Prompts / run, LLM calls, Tool calls, Quality, Time
   - Cells show [min–max] range when you hover

---

## Dashboard Features

### Columns in the "Before / after" table:

| Column | Meaning | Lower is better |
|--------|---------|-----------------|
| **Condition** | Practice label (e.g., `vague-prompt`, `scoped-prompt`) | — |
| **Runs** | Number of times you ran this condition | — |
| **Tokens / run** | Sum of input + output tokens across all LLM calls | ✓ Yes |
| **Prompts / run** | How many times you sent a message (includes follow-ups) | ✓ Yes |
| **LLM calls / run** | How many times Copilot called the LLM API | ✓ Yes |
| **Tool calls / run** | How many tools Copilot used (read_file, search, etc.) | ✓ Yes |
| **Cached in / run** | Tokens kept in cache from previous requests | ✓ Yes |
| **AIU / run** | Copilot's cost metric (`copilot_usage_nano_aiu` ÷ 1e9) | ✓ Yes |
| **Quality (1-5)** | Judge score or your stars | ✗ No (higher is better) |
| **Sec / run** | Wall time to get the final answer | ✓ Yes |

### Other dashboard controls:

- **Task filter**: Compare across conditions for a single task
- **Rows outside a run**: Prompts sent when no run is active (ignored)
- **First condition is baseline**: Other conditions show % change vs. it
- **⚠ warning**: Fewer than 3 runs per condition (small sample)

---

## Server API Endpoints

### Receiving telemetry

- **`POST /v1/traces`**  
  Receives OpenTelemetry trace data from VS Code (protobuf or JSON).
  - Parses spans, groups by `traceId`, totals metrics
  - Triggers judge if configured
  - Broadcasts to all SSE listeners

### Managing runs

- **`POST /config`** → Start a new run  
  Body: `{"condition": "...", "task": "..."}`  
  Returns: timestamp, condition, task, run number

- **`POST /stop`** → Stop the current run  
  Returns: labels with `run: 0` (disables counting)

- **`GET /config`** → Get current run state  
  Returns: last label + judge settings

### Rating & judging

- **`POST /rate`** → Submit user star rating  
  Body: `{"id": "trace-id", "rating": 5}`

### Exporting data

- **`GET /export.csv`** → Download all records as CSV  
  Columns: condition, task, run, time, model, prompt, llm_calls, tools, input_tokens, output_tokens, cache_read_tokens, aiu, duration_ms, human_rating, judge_correctness, judge_instruction_following, judge_reason

### Streaming

- **`GET /stream`** → Server-Sent Events connection  
  Browser subscribes once; receives all existing records + live updates

### Testing & debugging

- **`POST /demo`** → Inject fake trace data (test UI without Copilot)  
  Body: `{"model": "demo", "prompt": "...", "input_tokens": 1200, "output_tokens": 300}`

- **`GET /debug/spans`** → Latest 50 raw spans (debugging)

- **`GET /`** → Serve `index.html`

---

## Data Storage

### In-memory dictionaries:

```python
traces: dict[str, dict]     # trace_id → record
labels: list[dict]          # [{ts_ns, condition, task, run}, ...]
seen_spans: set[str]        # span IDs already processed (dedup)
listeners: set[Queue]       # connected SSE clients
recent_spans: list[dict]    # last 50 raw spans (debug)
```

### Lifetime:

- **Data persists** while the server is running
- **Lost on restart**: data is memory-only (no database)
- **Export before restarting**: use `/export.csv`

---

## Key Design Decisions

### Why OpenTelemetry?

- **Standard**: vendor-neutral, part of observability ecosystem
- **Structured**: spans = hierarchical events with attributes
- **Zero-setup**: VS Code Copilot emits OTLP/HTTP by default
- **Live streaming**: traces arrive as they complete, not batched

### Why in-memory?

- **Simple**: no database to set up or configure
- **Fast**: array/dict lookups, SSE broadcasts are instant
- **Transparent**: user controls export (CSV) and persistence

### Why a judge?

- **Objective**: removes human bias from quality scoring
- **Optional**: run without API key for manual ratings only
- **Async**: doesn't block the dashboard

### Why local-only?

- **Privacy**: prompt + answer stay on your machine (no cloud)
- **Security**: server binds to `127.0.0.1`, no auth (local only)
- **Speed**: everything is LAN, no network latency

---

## Files

| File | Purpose |
|---|---|
| [server.py](./server.py) | FastAPI server: OTLP receiver, span parser, judge caller, CSV exporter |
| [index.html](./index.html) | Browser dashboard: UI, SSE listener, real-time table updates |
| [requirements.txt](./requirements.txt) | Python packages: fastapi, uvicorn, opentelemetry, protobuf, python-dotenv |
| [.env](../.env) | Optional: `JUDGE_ENABLED`, `OPENROUTER_API_KEY`, `JUDGE_MODEL` |
| [EXPERIMENTS.md](./EXPERIMENTS.md) | Protocols for measuring three practices |
| [README.md](./README.md) | Setup, troubleshooting, column meanings |
| [HOW-IT-WORKS.md](./HOW-IT-WORKS.md) | This file: deep dive into architecture & flow |

---

## Running It

### Setup (once)
```bash
cd examples/copilot_monitor

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install packages
pip install -r requirements.txt

# Optional: enable judge
# cp .env.example .env
# Edit .env with your OPENROUTER_API_KEY
```

### Start the server
```bash
python -m uvicorn server:app --port 4318
```

Expect output:
```
INFO:     Uvicorn running on http://127.0.0.1:4318
INFO:     Application startup complete
```

Keep this terminal open.

### Configure VS Code

`Ctrl+Shift+P` → **Preferences: Open User Settings (JSON)**

Add inside the top-level `{}`:
```json
"github.copilot.chat.otel.enabled": true,
"github.copilot.chat.otel.exporterType": "otlp-http",
"github.copilot.chat.otel.otlpEndpoint": "http://localhost:4318",
"github.copilot.chat.otel.captureContent": true
```

Then reload: `Ctrl+Shift+P` → **Developer: Reload Window**.

### Verify connection

1. Open browser: `http://localhost:4318`
2. Send any Copilot Chat message
3. Watch server terminal for: `POST /v1/traces ... 200 OK`
4. New row appears in dashboard after Copilot finishes

---

## Troubleshooting

### "Page shows disconnected"
- Server not running? Start it with `uvicorn server:app --port 4318`

### "No `POST /v1/traces` in terminal"
- VS Code settings not applied? Recheck step 7 in README
- Port mismatch? Make sure `otlpEndpoint` matches your server port
- Copilot not instrumented? Check **Developer: Show Chat Debug View**

### "Rows show run `–` or don't appear"
- No active run? Press **Start new run** first
- Prompt outside a run? Prompts sent when no run is active are ignored

### "Judge returns HTTPError: 401"
- Missing or invalid `OPENROUTER_API_KEY`
- Set it in `.env` and restart the server

### "Judge returns HTTPError: 404"
- Invalid `JUDGE_MODEL`
- Copy the correct ID from https://openrouter.ai/models
- Restart the server

### "Data disappeared after restart"
- Data is in-memory only
- Export to CSV before restarting: click **Export CSV** on the dashboard

---

## Example Experiment: "Scoped Prompts vs. Vague Prompts"

### Condition 1: `vague-prompt` (baseline)
- Prompt: `add modulo to the calculator`
- Run it 3 times, note tokens/prompts/quality

### Condition 2: `scoped-prompt`
- Prompt: `In examples/calculator.py add modulo(a: float, b: float) -> float using %. Raise ValueError("Cannot take modulo by zero") when b == 0, same style as divide(). Do not touch main(). Reply with only the diff.`
- Run it 3 times

### Compare
- Does the scoped prompt use fewer tokens? Fewer prompts? Same quality or better?
- Export CSV and analyze

---

## Design Principles

1. **Minimize setup**: work out of the box with Copilot's OTLP export
2. **Local-first**: no cloud, no auth, no privacy concerns
3. **Transparent**: you see exactly what VS Code sends (raw spans in `/debug/spans`)
4. **Composable**: judge is optional, streaming is standard (SSE)
5. **Exportable**: data leaves as CSV, not locked in
