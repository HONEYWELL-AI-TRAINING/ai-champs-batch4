# Trace findings

Workflow(s) inspected: <which sample runs>
Date: <date>   Reader: <your name>

Cite a step you actually opened. "The agent looped" is not a finding. "Run b, spans 3, 5, 7, 9, 11: `get_build_status` called 5 times with the same `build_id`" is.

## Finding 1

- **Run / trace:** <e.g. run-b-loop>
- **Step(s):** <span names or numbers, e.g. execute_tool get_build_status, the 2nd to 5th call>
- **Pattern (deck s.7):** Loop | Retry storm | Wrong tool | Empty retrieval | Bloated payload
- **Evidence:** <numbers or text you read: tokens, repeated arguments, error text, empty result>
- **Likely cause:** <one sentence>
- **Proposed fix (one):** <what you would change, and where>
- **How I would know the fix worked:** <which number moves, in which direction>

## Finding 2

(same fields)

## Finding 3

(same fields)

## Something the script did not find

- **Run:** run-f-wrong-tool
- **What the user asked:**
- **What the agent called instead:**
- **Which tool should have been called, or should the agent have said it has none?**
