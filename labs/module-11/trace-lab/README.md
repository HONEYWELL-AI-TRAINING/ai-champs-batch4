# Module 11 Trace Lab

Read agent traces, spot failure patterns and token leaks, price a workflow, and decide whether to scale, tune, restrict or retire it.

The Python code uses the **standard library only**, so there is nothing to install to run the lab. `pytest` is needed only to run the tests.

> All sample traces, reviewer decisions and prices are **invented**. Don't quote them as your own results.

## Prerequisites

| Tool | Version | Needed for |
|---|---|---|
| Python | 3.10+ | everything |
| [uv](https://docs.astral.sh/uv/) | any recent | optional: running the tests |
| Node.js | 18+ | optional: `viewer-check` only |

## Setup

Run everything from this directory (`labs/module-11/trace-lab`).

```bash
# Optional: create a venv and install the dev tools (pytest)
uv sync
```

The sample traces are already in `traces/`. To regenerate them:

```bash
python -m tracelab.make_samples
```

## Run the lab

Commands below use `python`. If you used `uv sync`, use `uv run python ...` instead (or activate `.venv`).

### 1. Find failure patterns in the traces

```bash
python run_lab.py                  # reads traces/*.json
python run_lab.py trace.jsonl      # or your own agent's trace
```

This prints a **draft** findings table and writes it to `lab11/findings-draft.md`. It flags loops, retry storms, empty retrievals and bloated payloads. It can't detect a **wrong tool**; read the tool calls against the user's question yourself.

The draft is not your answer. Open each flagged step, then copy `templates/trace-findings.md` to `lab11/trace-findings.md` and write each finding in your own words, citing a run and a step.

### 2. Test a fix with "what if"

Estimate the savings if a tool's output were trimmed before the model saw it:

```bash
python -m tracelab.whatif traces/run-c-bloated.json --tool list_commits --to 600
```

This is an estimate. Re-run the real agent with the fix to confirm. Record the result in `templates/before-after.md`.

### 3. Measure quality and control signals

```bash
python -m tracelab.decisions data/reviewer-decisions.csv
```

CSV columns: `run, decision (accepted|edited|rejected), review_min, edit_min, later_defect, run_failed`.

### 4. Price the workflow (cost per accepted output)

```bash
mkdir -p lab11
cp templates/roi-inputs.json lab11/roi-inputs.json   # then edit it with your numbers
python roi_calc.py                                   # uses lab11/roi-inputs.json, else the template
python roi_calc.py path/to/inputs.json               # or point at any file
```

Every value in the template is a sample or placeholder. Replace what you can source and record where each number came from in `templates/roi-worksheet.md`. Keys starting with `_` are notes and are ignored. You can give `acceptance_rate` (0-1) instead of `accepted`.

### 5. Write up the decision

Copy the templates you need into `lab11/` and fill them in:

| Template | Purpose |
|---|---|
| `templates/trace-findings.md` | Findings, each citing a step in a trace |
| `templates/before-after.md` | Token counts before and after a fix |
| `templates/roi-worksheet.md` | Source and confidence for each ROI input |
| `templates/governance-checklist.md` | NIST AI RMF gap check for one workflow |
| `templates/decision.md` | Scale / Tune / Restrict / Retire, with evidence |
| `templates/leadership-onepager.md` | One-page summary for leadership |

### Bring your own agent's trace (Lab 03)

The Copilot runtime writes a JSON-lines trace (`trace.jsonl`). `run_lab.py` reads it directly. To open it in a viewer, convert it to OTLP/JSON first:

```bash
python -m tracelab.sdk_to_otlp trace.jsonl trace-otlp.json
```

`trace.jsonl` and `trace-otlp.json` are git-ignored.

## Sample traces

| File | Pattern |
|---|---|
| `run-a-healthy` | None (baseline) |
| `run-b-loop` | Loop: same tool called repeatedly |
| `run-c-bloated` | Bloated payload: one tool result inflates every later call |
| `run-d-retry-storm` | Retry storm: repeated failing tool calls |
| `run-e-empty-retrieval` | Empty retrieval: search returns nothing |
| `run-f-wrong-tool` | Wrong tool: only visible against the user's question |

## Check traces in a viewer (optional)

`viewer-check/` prints how [Agent Prism](https://github.com/evilmartians/agent-prism)'s OTLP adapter reads a trace (title, category, tokens and status per span).

```bash
cd viewer-check
npm install
node check.mjs ../traces/run-c-bloated.json
```

## Run the tests

```bash
uv run pytest
```

Or, without uv: `pip install pytest && python -m pytest`.

## Layout

```
trace-lab/
├── run_lab.py          # step 1: draft findings from traces
├── roi_calc.py         # step 4: cost per accepted output
├── tracelab/           # library + CLIs (analyze, whatif, decisions, roi, sdk_to_otlp, make_samples)
├── traces/             # sample OTLP/JSON runs
├── data/               # sample reviewer decisions
├── templates/          # write-up templates
├── tests/              # pytest suite
└── viewer-check/       # optional Node check against Agent Prism
```
