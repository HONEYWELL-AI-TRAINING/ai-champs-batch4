"""
Module 5 chatbot — FastAPI backend.

Endpoints:
- GET  /api/personas               → metadata for the persona picker
- POST /api/sessions               → create a new session
- POST /api/sessions/{sid}/chat    → send a message, stream the reply (SSE)
- DELETE /api/sessions/{sid}       → end a session
- GET  /api/sessions/{sid}         → inspect session state (debugging)
- GET  /healthz                    → liveness probe

Static files (the chat UI) are served from /static.
"""

from __future__ import annotations

import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

from .guardrails import SAFE_DECLINE, check_input, check_output
from .memory import (
    Strategy,
    apply_strategy,
    messages_token_estimate,
    should_rotate_summary,
)
from .personas import PERSONAS, get_system_prompt, persona_meta
from .sessions import store

load_dotenv()
client = OpenAI()
import os
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")


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

app = FastAPI(title="Module 5 Chatbot")

STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Schemas ───────────────────────────────────────────────────────────────────

class CreateSessionReq(BaseModel):
    persona: str = Field(default="nova")
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


@app.post("/api/sessions")
def create_session(req: CreateSessionReq) -> dict:
    if req.persona not in PERSONAS:
        raise HTTPException(400, f"unknown persona: {req.persona}")
    sess = store.create(req.persona, req.strategy, get_system_prompt(req.persona))
    return {
        "session_id": sess.sid,
        "persona": req.persona,
        "strategy": req.strategy,
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

    # ── Input guardrails (Layer 3) ──
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

    # ── Memory strategy (Layer 4) ──
    if sess.strategy == "summary" and should_rotate_summary(sess.history, summarize_every_turns=4):
        _rotate_summary(sess)

    prompt_messages = apply_strategy(sess.history, sess.strategy, window_pairs=4)
    in_tok_est = messages_token_estimate(prompt_messages)

    def event_stream():
        # Layer 5 — LLM call
        try:
            stream = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=prompt_messages,
                stream=True,
                **_completion_kwargs(CHAT_MODEL, max_tokens=400, temperature=0.6),
            )
        except Exception as exc:
            yield _sse({"event": "error", "error": str(exc)})
            return

        # Tell the client what we're working with
        yield _sse({
            "event": "meta",
            "persona": sess.persona_key,
            "strategy": sess.strategy,
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

        # Layer 6 — output guardrails
        sys_prompt = get_system_prompt(sess.persona_key)
        og = check_output(reply, sys_prompt)
        if not og["ok"]:
            yield _sse({"event": "guardrail", "stage": "output", "reason": og["reason"]})
            reply = SAFE_DECLINE

        sess.history.append({"role": "assistant", "content": reply})
        sess.turn_count += 1
        sess.total_input_tokens += in_tok_est
        sess.total_output_tokens += out_tok_est

        # Layer 7 — telemetry (we just log to stdout here)
        print(
            f"[turn] sid={sess.sid} persona={sess.persona_key} "
            f"strategy={sess.strategy} in≈{in_tok_est} out≈{out_tok_est}"
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
    resp = client.chat.completions.create(
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
