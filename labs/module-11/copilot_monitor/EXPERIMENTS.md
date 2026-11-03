# Practice experiments

Goal: show, with measured numbers, whether a Copilot best practice reduces **tokens per task**
and **prompts (iterations) per task** without lowering answer quality.

Use `examples/calculator.py` as the test repo. Run each condition **3 times** (the table flags
fewer than 3 runs with ⚠). Run the baseline first, then the practice.

## Protocol (every run)
1. In the monitor: set **Condition** and **Task**, press **Start new run**.
2. `git restore examples/calculator.py` (same starting state every time).
3. Open a **new chat**, same **model** and **mode** as every other run.
4. Do the task. If the answer is wrong or incomplete, send a follow-up (that is an "iteration", and it is counted).
5. Stop when the task is done. Rate the final answer with the stars if you like.

## Practice 1 - Specific, scoped prompt
Task name: `add-modulo`

| Condition | Prompt |
|---|---|
| `vague-prompt` (baseline) | `add modulo to the calculator` |
| `scoped-prompt` | `In examples/calculator.py add modulo(a: float, b: float) -> float using %. Raise ValueError("Cannot take modulo by zero") when b == 0, same style as divide(). Do not touch main(). Reply with only the diff.` |

Expect: fewer follow-ups and less exploration with the scoped prompt.

## Practice 2 - Attach the file instead of making the agent search
Task name: `add-modulo` (same scoped prompt for both, so only the context differs)

| Condition | How |
|---|---|
| `no-attachment` (baseline) | Agent mode, nothing attached |
| `file-attached` | Same prompt with `#file:examples/calculator.py` attached |

Expect: fewer tool calls (`read_file`, `semantic_search`) and fewer LLM calls per run.

## Practice 3 - Repository instructions
Task name: `add-modulo-style`

Create `.github/copilot-instructions.md` for the instruction runs only (delete it for baseline runs):

```
Python conventions for this repo:
- Every function has type hints on all parameters and the return value.
- Errors are raised as ValueError with a message starting "Cannot".
- Keep the diff minimal; do not modify unrelated functions.
```

Prompt for both conditions: `add a modulo function to examples/calculator.py`

| Condition | How |
|---|---|
| `no-instructions` (baseline) | File absent |
| `with-instructions` | File present |

Expect: without the file you will need a follow-up ("add type hints", "use the Cannot… message"),
which shows up as more prompts per run. The instructions file also adds a few input tokens to every
request, so it is a real trade-off and the table will show both sides.

## Reading the result
- Compare **Tokens / run** and **Prompts / run** against the baseline row, but check **Judge** too: a drop in tokens
  with a drop in quality is not an improvement.
- The judge only sees the prompt and the answer, not your instructions file, so for Practice 3 rely on
  **Prompts / run** (your follow-ups) rather than the judge score.
- Three runs per condition is a small sample. Report it as "in our runs", and use the min-max shown when
  hovering the tokens cell to show the spread.
- Keep everything else constant: model, mode, repo state, fresh chat.
