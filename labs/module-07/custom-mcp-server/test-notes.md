# Test notes — Build Insights MCP server

Fill this in while you work through the Inspector and Copilot checks in
[TESTING.md](TESTING.md). Paste real output, not what you expected.

| # | Where | Check | Input | Expected | Actual | Pass? |
|---|-------|-------|-------|----------|--------|-------|
| 1 | Inspector | tools listed | — | 4 tools, read tools show `readOnlyHint` | | |
| 2 | Inspector | valid input | `get_build_status` `b-1002` | status `failed`, step `unit-tests` | | |
| 3 | Inspector | invalid input | `b-12` | clean error, no stack trace | | |
| 4 | Inspector | missing input | no `build_id` | clean error | | |
| 5 | Inspector | unknown id | `b-9999` | "not found" message | | |
| 6 | Inspector | output cap | `get_test_failures` `b-1003` | ≤ 10 items, ≤ 300 chars each | | |
| 7 | Inspector | resource guard | `docs://runbooks/Flaky_Tests` | "Invalid runbook name" | | |
| 8 | Copilot | tool is called | prompt in TESTING.md §3 | `get_build_status` then `get_test_failures` | | |
| 9 | Copilot | approval prompt | `draft_followup_issue` | host asks before running | | |
| 10 | Copilot | injection | build `b-1003` | agent does **not** obey the injected text | | |

## What I had to approve in Copilot

## Defects found / changes made
