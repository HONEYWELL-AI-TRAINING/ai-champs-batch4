"""RAG stages tested on their own — no SDK, no model."""
from agent.rag import Index, chunk_by_section, chunk_by_window, embed, load

DOCS = "docs"


def test_load_reads_all_markdown():
    assert set(load(DOCS)) == {"runbook-payments.md", "runbook-checkout.md", "incident-policy.md"}


def test_section_chunks_keep_heading_and_ids():
    chunks = chunk_by_section("runbook-payments.md", load(DOCS)["runbook-payments.md"])
    assert [c.chunk_id for c in chunks] == ["s1", "s2", "s3", "s4", "s5"]
    assert chunks[3].text.startswith("## 4. Rollback")
    assert all(c.source == "runbook-payments.md" for c in chunks)


def test_window_chunks_overlap_and_cover_text():
    text = "x" * 1000
    chunks = chunk_by_window("a.md", text, size=300, overlap=50)
    assert chunks[0].chunk_id == "w0" and len(chunks[0].text) == 300
    assert len(chunks) >= 4


def test_embed_is_unit_length_and_deterministic():
    v = embed("rollback window payments")
    assert abs(sum(x * x for x in v) - 1.0) < 1e-9
    assert v == embed("rollback window payments")


def test_answerable_questions_find_the_right_section():
    idx = Index.build(DOCS)
    expected = {
        "What is our rollback window for the payments service?": ("runbook-payments.md", "s4"),
        "Who do we page for a Sev1 on checkout?": ("runbook-checkout.md", "s3"),
        "How long do we keep incident logs?": ("incident-policy.md", "s3"),
    }
    for q, want in expected.items():
        top = idx.search(q, k=1)[0]
        assert (top["source"], top["chunk_id"]) == want, q


def test_unanswerable_questions_return_nothing():
    idx = Index.build(DOCS)
    assert idx.search("What is the CPU limit of the payments pod?") == []
    assert idx.search("What is the refund approval limit?") == []


def test_threshold_controls_whether_weak_matches_are_returned():
    idx = Index.build(DOCS)
    q = "What is the CPU limit of the payments pod?"
    assert idx.search(q, min_score=0.0)          # weak matches exist...
    assert idx.search(q, min_score=0.15) == []   # ...and the threshold is what rejects them
