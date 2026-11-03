"""Simple RAG index (Lab 02): load -> chunk -> embed -> store, then retrieve top-k.

The "embedding" is a hashed bag-of-words vector so the lab runs with no model, no
key and no network. It is a STAND-IN: it only matches shared words, where a real
embedding model also matches paraphrases. Swap `embed()` for a real model later;
nothing else in this file changes.
"""
import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path

DIM = 4096
STOP = {"the", "a", "an", "is", "of", "to", "for", "and", "or", "in", "on", "what", "our", "do",
        "does", "how", "who", "are", "we", "it", "this", "that", "with", "at", "be", "by", "as", "from"}


@dataclass(frozen=True)
class Chunk:
    text: str
    source: str      # metadata: file name
    chunk_id: str    # metadata: section number ("s4") or window number ("w2")


def tokens(text):
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOP]


def embed(text):
    """Text -> unit vector. (Stand-in for a real embedding model.)"""
    vec = [0.0] * DIM
    for tok in tokens(text):
        vec[int(hashlib.md5(tok.encode()).hexdigest(), 16) % DIM] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def load(folder):
    """LOAD: read every markdown file in the folder."""
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(Path(folder).glob("*.md"))}


def chunk_by_section(source, text):
    """CHUNK (default): one chunk per '## ' section; the heading stays so the chunk says where it is from."""
    out = []
    for part in re.split(r"(?m)^(?=## )", text):
        part = part.strip()
        if part.startswith("## "):
            number = re.match(r"## (\d+)\.", part)
            out.append(Chunk(part, source, f"s{number.group(1)}" if number else f"c{len(out)}"))
    return out


def chunk_by_window(source, text, size=300, overlap=50):
    """CHUNK (experiment): fixed-size character windows. Ignores structure on purpose."""
    out, start, n = [], 0, 0
    while start < len(text):
        out.append(Chunk(text[start:start + size].strip(), source, f"w{n}"))
        start += size - overlap
        n += 1
    return [c for c in out if c.text]


class Index:
    def __init__(self, chunks):
        self.chunks = chunks
        self.vectors = [embed(c.text) for c in chunks]  # STORE: vectors and source live together

    @classmethod
    def build(cls, folder, strategy="section", size=300, overlap=50):
        chunks = []
        for name, text in load(folder).items():
            if strategy == "section":
                chunks += chunk_by_section(name, text)
            else:
                chunks += chunk_by_window(name, text, size, overlap)
        return cls(chunks)

    def search(self, query, k=4, min_score=0.15):
        """RETRIEVE: top-k chunks by cosine similarity; anything below min_score is dropped,
        so an unanswerable question can return []."""
        q = embed(query)
        scored = [(sum(a * b for a, b in zip(q, v)), c) for v, c in zip(self.vectors, self.chunks)]
        scored.sort(key=lambda s: s[0], reverse=True)
        return [{"text": c.text, "source": c.source, "chunk_id": c.chunk_id, "score": round(s, 3)}
                for s, c in scored[:k] if s >= min_score]
