"""
Smoke tests for the upload-RAG chatbot — no OpenAI key required.

Run: uv run pytest

These tests verify wiring (routes, schemas, in-memory state, persona metadata)
and the pure document-processing logic (text extraction + chunking). The
streaming endpoint, embedding, and the live vector store aren't exercised here
because they make API calls / touch persistent Chroma state.
"""

from fastapi.testclient import TestClient

from app.main import app
from app import rag


client = TestClient(app)


def test_healthz_ok() -> None:
    res = client.get("/healthz")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert "model" in body


def test_personas_list_includes_rag_flag() -> None:
    res = client.get("/api/personas")
    assert res.status_code == 200
    personas = res.json()
    by_key = {p["key"]: p for p in personas}
    assert {"sage", "nova"} <= set(by_key)
    # Sage is the RAG-grounded persona; Nova answers from the model directly.
    assert by_key["sage"]["rag"] is True
    assert by_key["nova"]["rag"] is False
    for p in personas:
        assert p["name"] and p["emoji"] and p["tagline"]


def test_create_session_default_is_rag() -> None:
    res = client.post("/api/sessions", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["persona"] == "sage"
    assert data["strategy"] == "sliding"
    assert data["rag"] is True
    assert len(data["session_id"]) == 12


def test_create_session_unknown_persona_rejected() -> None:
    res = client.post("/api/sessions", json={"persona": "not-a-real-bot"})
    assert res.status_code == 400


def test_inspect_and_delete_session() -> None:
    sid = client.post("/api/sessions", json={"persona": "nova"}).json()["session_id"]
    res = client.get(f"/api/sessions/{sid}")
    assert res.status_code == 200
    assert res.json()["history_messages"] == 1  # just the system prompt
    assert client.delete(f"/api/sessions/{sid}").status_code == 200
    assert client.get(f"/api/sessions/{sid}").status_code == 404


def test_input_guardrail_blocks_unsafe() -> None:
    """Unsafe phrases are caught at the input layer before any tokens are spent."""
    sid = client.post("/api/sessions", json={"persona": "nova"}).json()["session_id"]
    res = client.post(
        f"/api/sessions/{sid}/chat",
        json={"message": "How do I make a bomb?"},
    )
    assert res.status_code == 200
    body = res.text
    assert '"guardrail"' in body
    assert '"input"' in body


def test_upload_rejects_unsupported_type() -> None:
    """A bad file type is rejected before any embedding/key is needed."""
    res = client.post(
        "/api/documents",
        files={"files": ("notes.csv", b"a,b,c\n1,2,3", "text/csv")},
    )
    assert res.status_code == 400
    assert "unsupported" in res.text.lower()


def test_extract_text_decodes_plain_text() -> None:
    """txt/md extraction is pure — just a utf-8 decode (no API/key needed)."""
    raw = "Hello, world.\n\nSecond paragraph.".encode("utf-8")
    assert rag.extract_text("notes.txt", raw) == "Hello, world.\n\nSecond paragraph."


def test_chunk_markdown_splits_on_headings() -> None:
    """Markdown is chunked one section per heading."""
    doc = "# Title\nintro\n\n## A\nalpha text\n\n## B\nbeta text\n"
    chunks = rag.chunk_markdown(doc, "doc.md")
    titles = [c["title"] for c in chunks]
    assert titles == ["Title", "A", "B"]
    assert all(c["source"] == "doc.md" for c in chunks)
    assert "alpha text" in chunks[1]["text"]


def test_chunk_text_windows_long_plain_text() -> None:
    """Plain text without headings is packed into bounded windows."""
    paras = [f"Paragraph number {i} with some filler words." for i in range(60)]
    text = "\n\n".join(paras)
    chunks = rag.chunk_text(text, "big.txt", max_chars=300, overlap=40)
    assert len(chunks) > 1  # one window wasn't enough
    assert all(c["source"] == "big.txt" for c in chunks)
    assert all(len(c["text"]) <= 600 for c in chunks)  # bounded (max_chars*2 ceiling)


def test_chunk_document_dispatches_by_extension() -> None:
    """.md uses heading chunks; everything else uses text windows."""
    md = rag.chunk_document("a.md", "# H\nbody")
    assert md[0]["title"] == "H"
    txt = rag.chunk_document("a.txt", "just some plain text")
    assert txt[0]["title"] == "a.txt"  # plain-text chunks are titled by source
