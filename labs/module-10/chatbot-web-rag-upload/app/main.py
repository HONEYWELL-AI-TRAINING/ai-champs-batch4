"""
Module 6 RAG chatbot (upload edition) — FastAPI backend.

This is the Module 5 streaming chatbot enhanced with Retrieval-Augmented
Generation, where the knowledge base is built from files the user UPLOADS at
runtime (.txt, .md, .pdf). When the active persona is RAG-enabled (Sage), each
turn embeds the user's question, retrieves the top-k most relevant chunks of the
uploaded documents from a Chroma vector store, and injects them as grounding
context so the model answers from those documents instead of its parametric
memory.

Endpoints:
- GET    /api/personas              → metadata for the persona picker (incl. `rag`)
- GET    /api/documents             → list indexed files (source + chunk count)
- POST   /api/documents             → upload + index one or more files (multipart)
- POST   /api/documents/samples     → index the bundled sample docs (one-click demo)
- DELETE /api/documents             → clear the whole knowledge base
- DELETE /api/documents/{source}    → remove one file from the index
- POST   /api/sessions              → create a new session
- POST   /api/sessions/{sid}/chat   → send a message, stream the reply (SSE)
- DELETE /api/sessions/{sid}        → end a session
- GET    /api/sessions/{sid}        → inspect session state (debugging)
- GET    /healthz                   → liveness probe

Static files (the chat UI) are served from /static.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

from . import rag
from .guardrails import SAFE_DECLINE, check_input, check_output
from .memory import (
    Strategy,
    apply_strategy,
    messages_token_estimate,
    should_rotate_summary,
)
from .personas import PERSONAS, get_system_prompt, persona_meta, persona_uses_rag
from .sessions import store

load_dotenv()
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "3"))

_client: OpenAI | None = None


def _chat_client() -> OpenAI:
    # Lazy so the app imports (and the smoke tests run) without an API key.
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def _completion_kwargs(model: str, max_tokens: int, temperature: float | None = None) -> dict:
    # GPT-5 family uses `max_completion_tokens` and rejects custom `temperature`.
    # It also spends reasoning tokens out of that same budget, so a small cap can
    # be fully consumed by reasoning, leaving zero visible output. Keep reasoning
    # minimal and give the budget headroom so the reply actually streams.
    if model.startswith("gpt-5"):
        return {
            "max_completion_tokens": max(max_tokens, 2000),
            "reasoning_effort": "minimal",
        }
    kwargs: dict = {"max_tokens": max_tokens}
    if temperature is not None:
        kwargs["temperature"] = temperature
    return kwargs


app = FastAPI(title="Module 6 RAG Chatbot")

STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Schemas ───────────────────────────────────────────────────────────────────

class CreateSessionReq(BaseModel):
    persona: str = Field(default="sage")
    strategy: Strategy = Field(default="sliding")


class ChatReq(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "model": CHAT_MODEL}


@app.get("/api/personas")
def list_personas() -> list[dict]:
    return persona_meta()


# ── Documents (the upload → index knowledge base) ───────────────────────────────

@app.get("/api/documents")
def list_documents() -> dict:
    """List the files currently in the vector store, with per-file chunk counts."""
    try:
        docs = rag.list_documents()
    except Exception as exc:
        raise HTTPException(500, f"could not read index: {exc}")
    return {"documents": docs, "total_chunks": sum(d["chunks"] for d in docs)}


@app.post("/api/documents")
async def upload_documents(files: list[UploadFile] = File(...)) -> dict:
    """
    Upload one or more files, extract their text, chunk, embed, and index them.

    Each file is read into memory and handed to the RAG pipeline. Unsupported
    types or empty files are reported per-file rather than failing the batch.
    """
    indexed: list[dict] = []
    errors: list[dict] = []
    for f in files:
        raw = await f.read()
        if not raw:
            errors.append({"source": f.filename, "error": "empty file"})
            continue
        try:
            indexed.append(rag.index_document(f.filename, raw))
        except ValueError as exc:
            errors.append({"source": f.filename, "error": str(exc)})
        except Exception as exc:  # embedding / store failures (e.g. missing key)
            errors.append({"source": f.filename, "error": f"indexing failed: {exc}"})

    if not indexed and errors:
        # Nothing made it in — surface the first problem as a 400 for the UI.
        raise HTTPException(400, errors[0]["error"])

    return {"indexed": indexed, "errors": errors, "documents": rag.list_documents()}


@app.post("/api/documents/samples")
def index_samples() -> dict:
    """One-click demo: index the bundled sample docs in data/."""
    try:
        indexed = rag.index_samples()
    except Exception as exc:
        raise HTTPException(500, f"could not index samples: {exc}")
    return {"indexed": indexed, "documents": rag.list_documents()}


@app.delete("/api/documents")
def clear_documents() -> dict:
    """Wipe the entire knowledge base for a clean demo."""
    rag.clear_all()
    return {"cleared": True, "documents": []}


@app.delete("/api/documents/{source}")
def delete_document(source: str) -> dict:
    """Remove a single file's chunks from the index."""
    rag.remove_document(source)
    return {"removed": source, "documents": rag.list_documents()}


@app.post("/api/sessions")
def create_session(req: CreateSessionReq) -> dict:
    if req.persona not in PERSONAS:
        raise HTTPException(400, f"unknown persona: {req.persona}")
    sess = store.create(req.persona, req.strategy, get_system_prompt(req.persona))
    return {
        "session_id": sess.sid,
        "persona": req.persona,
        "strategy": req.strategy,
        "rag": persona_uses_rag(req.persona),
    }


@app.get("/api/sessions/{sid}")
def get_session(sid: str) -> dict:
    sess = store.get(sid)
    if sess is None:
        raise HTTPException(404, "session not found")
    return {
        "session_id": sess.sid,
        "persona": sess.persona_key,
        "strategy": sess.strategy,
        "turn_count": sess.turn_count,
        "history_messages": len(sess.history),
        "total_input_tokens": sess.total_input_tokens,
        "total_output_tokens": sess.total_output_tokens,
    }


@app.delete("/api/sessions/{sid}")
def end_session(sid: str) -> dict:
    store.delete(sid)
    return {"ended": sid}


@app.post("/api/sessions/{sid}/chat")
def chat(sid: str, req: ChatReq) -> StreamingResponse:
    sess = store.get(sid)
    if sess is None:
        raise HTTPException(404, "session not found — start a new one")

    # ── Input guardrails ──
    guard = check_input(req.message)
    if not guard["ok"]:
        def safe_stream():
            yield _sse({"event": "guardrail", "stage": "input", "reason": guard["reason"]})
            for word in SAFE_DECLINE.split():
                yield _sse({"event": "delta", "delta": word + " "})
            yield _sse({"event": "done", "input_tokens": 0, "output_tokens": 0})
        return StreamingResponse(safe_stream(), media_type="text/event-stream")

    user_msg = guard["redacted"]
    sess.history.append({"role": "user", "content": user_msg})

    # ── Memory strategy ──
    if sess.strategy == "summary" and should_rotate_summary(sess.history, summarize_every_turns=4):
        _rotate_summary(sess)

    use_rag = persona_uses_rag(sess.persona_key)

    def event_stream():
        prompt_messages = apply_strategy(sess.history, sess.strategy, window_pairs=4)

        # ── Retrieval (RAG) — embed the question, pull top-k grounding chunks ──
        if use_rag:
            try:
                hits = rag.retrieve(user_msg, top_k=RAG_TOP_K)
            except Exception as exc:
                yield _sse({"event": "error", "error": f"retrieval failed: {exc}"})
                return

            # Show the user exactly what grounded the answer.
            yield _sse({
                "event": "sources",
                "hits": [
                    {
                        "n": i,
                        "source": h["source"],
                        "title": h["title"],
                        "score": h["score"],
                        "preview": h["text"][:260],
                    }
                    for i, h in enumerate(hits, 1)
                ],
            })

            if hits:
                context_block = rag.build_context_block(hits)
                context_msg = {
                    "role": "system",
                    "content": (
                        "Use ONLY the following retrieved context to answer the "
                        "user's question. Cite the passages you use as [n]. If the "
                        "answer is not in the context, say you don't know.\n\n"
                        f"{context_block}"
                    ),
                }
                # Inject right after the persona system prompt.
                prompt_messages.insert(1, context_msg)

        in_tok_est = messages_token_estimate(prompt_messages)

        # ── LLM call ──
        try:
            stream = _chat_client().chat.completions.create(
                model=CHAT_MODEL,
                messages=prompt_messages,
                stream=True,
                **_completion_kwargs(CHAT_MODEL, max_tokens=400, temperature=0.6),
            )
        except Exception as exc:
            yield _sse({"event": "error", "error": str(exc)})
            return

        yield _sse({
            "event": "meta",
            "persona": sess.persona_key,
            "strategy": sess.strategy,
            "rag": use_rag,
            "messages_in_prompt": len(prompt_messages),
            "input_tokens_est": in_tok_est,
        })

        collected: list[str] = []
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                collected.append(delta)
                yield _sse({"event": "delta", "delta": delta})

        reply = "".join(collected)
        out_tok_est = len(reply.split())

        # ── Output guardrails ──
        sys_prompt = get_system_prompt(sess.persona_key)
        og = check_output(reply, sys_prompt)
        if not og["ok"]:
            yield _sse({"event": "guardrail", "stage": "output", "reason": og["reason"]})
            reply = SAFE_DECLINE

        sess.history.append({"role": "assistant", "content": reply})
        sess.turn_count += 1
        sess.total_input_tokens += in_tok_est
        sess.total_output_tokens += out_tok_est

        print(
            f"[turn] sid={sess.sid} persona={sess.persona_key} "
            f"strategy={sess.strategy} rag={use_rag} in≈{in_tok_est} out≈{out_tok_est}"
        )

        yield _sse({
            "event": "done",
            "input_tokens": in_tok_est,
            "output_tokens": out_tok_est,
            "turn_count": sess.turn_count,
            "total_input_tokens": sess.total_input_tokens,
            "total_output_tokens": sess.total_output_tokens,
        })

    return StreamingResponse(event_stream(), media_type="text/event-stream")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _rotate_summary(sess) -> None:
    """
    Replace the oldest mid-conversation turns with a model-generated summary.
    Keeps the system prompt and the last 4 messages verbatim.
    """
    keep_recent = 4
    rest = [m for m in sess.history if m["role"] != "system"]
    if len(rest) <= keep_recent:
        return
    middle = rest[: -keep_recent]
    recent = rest[-keep_recent:]

    body = "\n".join(f"{m['role']}: {m['content']}" for m in middle)
    resp = _chat_client().chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content":
                "Summarize the conversation below in 4–6 bullet points. "
                "Preserve names, IDs, dates, decisions, and unresolved questions. "
                "This summary will replace the verbatim turns."},
            {"role": "user", "content": body},
        ],
        **_completion_kwargs(CHAT_MODEL, max_tokens=240),
    )
    summary = resp.choices[0].message.content or ""

    system_msg = next(m for m in sess.history if m["role"] == "system")
    sess.history = [
        system_msg,
        {"role": "system", "content": f"[Earlier conversation summary]\n{summary}"},
        *recent,
    ]
