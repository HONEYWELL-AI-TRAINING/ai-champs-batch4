# Runbook: flaky tests

1. Re-run the failing job once. If it passes, label the build `flaky`.
2. If the same test fails twice in a week, open a follow-up issue.
3. Never disable a test without a linked issue.
