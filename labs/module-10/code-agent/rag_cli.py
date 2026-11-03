"""Lab 02: the RAG pipeline on its own, with no model — so you can SEE each stage.

  python rag_cli.py index                        # load -> chunk -> embed -> store, print what was built
  python rag_cli.py query "rollback window for payments" [--k 4] [--min-score 0.15] [--window 300]
"""
import argparse

from agent.rag import Index, embed, load


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["index", "query"])
    p.add_argument("text", nargs="?")
    p.add_argument("--docs", default="docs")
    p.add_argument("--k", type=int, default=4)
    p.add_argument("--min-score", type=float, default=0.15)
    p.add_argument("--window", type=int, default=0, help="use fixed windows of N chars instead of sections")
    a = p.parse_args()

    strategy = "window" if a.window else "section"
    idx = Index.build(a.docs, strategy=strategy, size=a.window or 300)

    if a.command == "index":
        docs = load(a.docs)
        print(f"LOAD   : {len(docs)} documents -> {', '.join(docs)}")
        print(f"CHUNK  : {len(idx.chunks)} chunks (strategy={strategy})")
        for c in idx.chunks:
            print(f"   {c.source:<22} {c.chunk_id:<4} {len(c.text):>4} chars  {c.text.splitlines()[0][:50]}")
        nz = sum(1 for _ in idx.vectors[0] if _)
        print(f"EMBED  : each chunk -> {len(idx.vectors[0])}-dim vector ({nz} non-zero in the first one)")
        print(f"STORE  : {len(idx.vectors)} vectors kept next to (source, chunk_id)")
        return

    if not a.text:
        p.error("query needs a question")
    hits = idx.search(a.text, k=a.k, min_score=a.min_score)
    print(f"QUERY  : {a.text!r}  (k={a.k}, min_score={a.min_score}, strategy={strategy})")
    if not hits:
        print("RETRIEVE: [] — nothing cleared the threshold. The agent should say it could not find this.")
    for h in hits:
        print(f"  {h['score']:.3f}  {h['source']} {h['chunk_id']}: {h['text'].splitlines()[-1][:90]}")


if __name__ == "__main__":
    main()
