"""
RAG layer — same retrieval pipeline as chatbot-web-rag, but the knowledge base
is built from files the *user uploads at runtime* (.txt, .md, .pdf) instead of a
fixed data/ directory.

Pipeline (Guide 06 §4-§6):
    upload file -> extract text -> chunk -> embed -> store in Chroma
    user question -> embed -> top-k nearest -> ground the answer

The Chroma collection is persistent under ./chroma_store, so indexed documents
survive a restart. Everything is lazy: nothing touches OpenAI or Chroma until
the first upload or retrieval, so the app imports (and the smoke tests run)
without an API key.
"""

from __future__ import annotations

import os
import re
from io import BytesIO
from pathlib import Path

import chromadb
from openai import OpenAI

DATA_DIR = Path(__file__).parent.parent / "data"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_store"
COLLECTION = "uploaded_docs"

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# The file types the upload pipeline understands.
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}

_client: OpenAI | None = None
_db = None
_collection = None


def _openai() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def embed(texts: list[str]) -> list[list[float]]:
    """Embed with OpenAI so documents and queries live in one vector space."""
    resp = _openai().embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in resp.data]


# ── Text extraction ────────────────────────────────────────────────────────────

def extract_text(filename: str, raw: bytes) -> str:
    """Pull plain text out of an uploaded file, picking a reader by extension."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return _extract_pdf(raw)
    # .txt and .md are already text — decode and let the chunker handle layout.
    return raw.decode("utf-8", errors="replace")


def _extract_pdf(raw: bytes) -> str:
    """Extract text from a PDF, one block per page. Imported lazily so the app
    (and the no-key smoke tests) load even if pypdf isn't installed yet."""
    from pypdf import PdfReader

    reader = PdfReader(BytesIO(raw))
    return "\n\n".join((page.extract_text() or "").strip() for page in reader.pages)


# ── Chunking ───────────────────────────────────────────────────────────────────

def chunk_markdown(text: str, source: str) -> list[dict]:
    """
    Split a markdown doc into retrievable chunks, one per heading section.

    Each chunk keeps its heading so a retrieved passage carries enough context
    to stand alone.
    """
    chunks: list[dict] = []
    sections = re.split(r"\n(?=#{1,6}\s)", text.strip())
    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading = re.match(r"#{1,6}\s+(.*)", section)
        title = heading.group(1).strip() if heading else source
        chunks.append({"text": section, "source": source, "title": title})
    return chunks


def chunk_text(text: str, source: str, max_chars: int = 1200, overlap: int = 150) -> list[dict]:
    """
    Split plain text (.txt / extracted PDF) into overlapping windows.

    Markdown has headings to split on; plain text doesn't, so we pack whole
    paragraphs into ~max_chars windows and carry a little overlap between them so
    a fact that straddles a boundary still lands in one chunk.
    """
    text = text.strip()
    if not text:
        return []

    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    windows: list[str] = []
    buf = ""
    for para in paragraphs:
        if buf and len(buf) + len(para) + 2 > max_chars:
            windows.append(buf)
            tail = buf[-overlap:] if overlap else ""
            buf = f"{tail}\n\n{para}".strip() if tail else para
        else:
            buf = f"{buf}\n\n{para}" if buf else para
    if buf:
        windows.append(buf)

    # Hard-split any single window that's still way over budget (one giant para).
    final: list[str] = []
    for w in windows:
        if len(w) <= max_chars * 2:
            final.append(w)
        else:
            step = max_chars - overlap
            final.extend(w[i:i + max_chars] for i in range(0, len(w), step))

    return [
        {"text": w.strip(), "source": source, "title": source}
        for w in final
        if w.strip()
    ]


def chunk_document(filename: str, text: str) -> list[dict]:
    """Pick a chunking strategy by file type: headings for .md, windows otherwise."""
    if Path(filename).suffix.lower() == ".md":
        return chunk_markdown(text, filename)
    return chunk_text(text, filename)


# ── Collection management ───────────────────────────────────────────────────────

def get_collection():
    """Open (or create) the persistent Chroma collection and cache it."""
    global _db, _collection
    if _collection is not None:
        return _collection
    _db = chromadb.PersistentClient(path=str(CHROMA_DIR))
    _collection = _db.get_or_create_collection(
        COLLECTION, metadata={"hnsw:space": "cosine"}
    )
    return _collection


def index_document(filename: str, raw: bytes) -> dict:
    """
    Extract, chunk, embed, and add one uploaded file to the collection.

    Re-uploading a file with the same name replaces the old version. Returns a
    small summary: {"source", "chunks"}.
    """
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"unsupported file type '{ext or '(none)'}' — use .txt, .md, or .pdf")

    text = extract_text(filename, raw)
    chunks = chunk_document(filename, text)
    if not chunks:
        raise ValueError("no readable text found in this file")

    col = get_collection()
    col.delete(where={"source": filename})  # drop any previous version
    col.add(
        ids=[f"{filename}::{i}" for i in range(len(chunks))],
        documents=[c["text"] for c in chunks],
        embeddings=embed([c["text"] for c in chunks]),
        metadatas=[{"source": filename, "title": c["title"]} for c in chunks],
    )
    return {"source": filename, "chunks": len(chunks)}


def list_documents() -> list[dict]:
    """Return the indexed files and how many chunks each contributed."""
    col = get_collection()
    if col.count() == 0:
        return []
    got = col.get(include=["metadatas"])
    counts: dict[str, int] = {}
    for meta in got["metadatas"]:
        src = meta.get("source", "?")
        counts[src] = counts.get(src, 0) + 1
    return [{"source": s, "chunks": n} for s, n in sorted(counts.items())]


def remove_document(source: str) -> None:
    """Delete every chunk belonging to one file."""
    get_collection().delete(where={"source": source})


def clear_all() -> None:
    """Wipe the whole knowledge base for a clean demo."""
    global _collection
    get_collection()
    if _db is not None:
        _db.delete_collection(COLLECTION)
    _collection = None


def index_samples() -> list[dict]:
    """Index the bundled sample docs in data/ — the one-click demo shortcut."""
    results: list[dict] = []
    for path in sorted(DATA_DIR.glob("*")):
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            results.append(index_document(path.name, path.read_bytes()))
    return results


# ── Retrieval ───────────────────────────────────────────────────────────────────

def retrieve(question: str, top_k: int = 3) -> list[dict]:
    """Embed the question and return the top-k most similar chunks with scores."""
    col = get_collection()
    if col.count() == 0:
        return []
    q_vec = embed([question])[0]
    res = col.query(
        query_embeddings=[q_vec],
        n_results=min(top_k, col.count()),
        include=["documents", "metadatas", "distances"],
    )
    hits: list[dict] = []
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        hits.append({
            "text": doc,
            "source": meta.get("source", "?"),
            "title": meta.get("title", ""),
            "score": round(1 - dist, 3),  # cosine distance -> similarity
        })
    return hits


def build_context_block(hits: list[dict]) -> str:
    """Format retrieved chunks as a numbered grounding block for the prompt."""
    return "\n\n".join(
        f"[{i}] (source: {h['source']})\n{h['text']}" for i, h in enumerate(hits, 1)
    )
