"""Lab 02 driver: five fixed questions, UNGROUNDED then GROUNDED, written to baseline.md,
grounded.md and comparison.md.

  python run_lab.py            -> your Copilot sign-in (10 short sessions, spends your usage allowance)
  python run_lab.py --offline  -> scripted local model (plumbing only; says nothing about real answers)
  python run_lab.py --strict   -> same, with the stronger grounding instructions; writes *-strict.md files
"""
import asyncio
import sys

from agent.agent import ask, new_client

QUESTIONS = [  # (question, expected source or None when the docs cannot answer it)
    ("What is our rollback window for the payments service?", "runbook-payments.md"),
    ("Who do we page for a Sev1 on checkout?", "runbook-checkout.md"),
    ("How long do we keep incident logs?", "incident-policy.md"),
    ("What is the CPU limit of the payments pod?", None),
    ("What is the refund approval limit?", None),
]


def verdict(expected, answer_text):
    low = answer_text.lower()
    said_not_found = "couldn't find" in low or "could not find" in low or "not found" in low
    if expected is None:
        return "OK (declined)" if said_not_found else "CHECK: answered an unanswerable question"
    if expected in answer_text:
        return "OK (cited)"
    return "CHECK: no citation" if not said_not_found else "CHECK: declined but docs have it"


async def run_all(strict=False):
    rows = []
    async with new_client() as client:
        for q, expected in QUESTIONS:
            base = await ask(client, q)
            grounded = await ask(client, q, docs="docs", strict=strict)
            rows.append((q, expected, base, grounded))
    return rows


def write(rows, suffix=""):
    for name, idx in ((f"baseline{suffix}.md", 2), (f"grounded{suffix}.md", 3)):
        with open(name, "w", encoding="utf-8") as f:
            f.write(f"# {name[:-3].title()} answers\n\n")
            for r in rows:
                f.write(f"## {r[0]}\n\n{r[idx].text}\n\nTool calls: {[t['tool'] for t in r[idx].trace]}\n"
                        f"Usage: {r[idx].usage}\n\n")
    short = lambda s: s.replace("\n", " ").replace("|", "/")[:90]
    with open(f"comparison{suffix}.md", "w", encoding="utf-8") as f:
        f.write("| # | Question | Expected | Baseline | Grounded | Searched? | Verdict | Failure stage (you fill in) |\n")
        f.write("|---|----------|----------|----------|----------|-----------|---------|-----------------------------|\n")
        for i, (q, expected, base, grounded) in enumerate(rows, 1):
            searched = "yes" if any(t["tool"] == "search_docs" for t in grounded.trace) else "NO"
            f.write(f"| {i} | {q} | {expected or 'not in docs'} | {short(base.text)} | {short(grounded.text)} "
                    f"| {searched} | {verdict(expected, grounded.text)} | |\n")


if __name__ == "__main__":
    if "--offline" in sys.argv:
        import mock_model
        mock_model.use_offline()
    strict = "--strict" in sys.argv
    suffix = "-strict" if strict else ""
    write(asyncio.run(run_all(strict)), suffix)
    print(open(f"comparison{suffix}.md", encoding="utf-8").read())
