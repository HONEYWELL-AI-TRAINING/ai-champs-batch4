"""Lab 02: measure RETRIEVAL alone (no model, no cost) so you can tune chunking, k and the threshold.

  python eval_retrieval.py                      # section chunks, k=4, min_score=0.15
  python eval_retrieval.py --window 300 --k 2   # try fixed windows, fewer results
"""
import argparse

from agent.rag import Index

# (question, expected source, expected chunk id)  — None means the docs cannot answer it.
CASES = [
    ("What is our rollback window for the payments service?", ("runbook-payments.md", "s4")),
    ("Who do we page for a Sev1 on checkout?", ("runbook-checkout.md", "s3")),
    ("How long do we keep incident logs?", ("incident-policy.md", "s3")),
    ("What is the CPU limit of the payments pod?", None),
    ("What is the refund approval limit?", None),
]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--docs", default="docs")
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--min-score", type=float, default=0.15)
    p.add_argument("--window", type=int, default=0)
    a = p.parse_args()
    idx = Index.build(a.docs, strategy="window" if a.window else "section", size=a.window or 300)

    ok = 0
    print(f"{len(idx.chunks)} chunks | k={a.k} min_score={a.min_score} "
          f"strategy={'window' if a.window else 'section'}\n")
    for q, expected in CASES:
        hits = idx.search(q, k=a.k, min_score=a.min_score)
        top = (hits[0]["source"], hits[0]["chunk_id"]) if hits else None
        if expected is None:
            good = not hits
            note = "correctly returned nothing" if good else f"RETURNED {top} score {hits[0]['score']} (should be empty)"
        elif a.window:  # window ids differ from section ids, so judge by source file
            good = any(h["source"] == expected[0] for h in hits)
            note = f"source hit: {good} (top: {top})"
        else:
            good = (expected in [(h["source"], h["chunk_id"]) for h in hits])
            rank = next((i + 1 for i, h in enumerate(hits) if (h["source"], h["chunk_id"]) == expected), None)
            note = f"expected {expected} found at rank {rank}" if rank else f"expected {expected} NOT retrieved (top: {top})"
        ok += good
        print(f"[{'PASS' if good else 'FAIL'}] {q}\n        {note}")
    print(f"\n{ok}/{len(CASES)} passed")


if __name__ == "__main__":
    main()
