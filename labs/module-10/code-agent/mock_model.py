"""Scripted OpenAI-compatible /v1/chat/completions server for OFFLINE lab runs.

It is NOT a language model. It exists so the SDK plumbing (tools, loop, hooks,
permissions, retrieval) can be exercised with no account, no cost and no network.
Rules:
  * last message is a tool result -> write a final answer from it
  * last message is the user       -> call a tool if one fits, else answer from "memory"
Use it via the SDK's BYOK `provider=` option (see agent/agent.py, LAB_PROVIDER_URL).
"""
import json
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LOG = []
LOOP_FOREVER = False   # runaway mode: keep calling a tool whatever it returns (tests the step cap)
TOOLS_SEEN = []        # tool names the runtime offered on each request (tests the allow-list)


def _tool_names(body):
    return {t["function"]["name"] for t in body.get("tools", [])}


def _text_of(content):
    if isinstance(content, list):
        return " ".join(p.get("text", "") for p in content if isinstance(p, dict))
    return content or ""


def decide(body):
    """Return ('tool', name, args) or ('text', answer)."""
    msgs = body.get("messages", [])
    last = msgs[-1]
    names = _tool_names(body)
    TOOLS_SEEN.append(sorted(names))
    if LOOP_FOREVER and "get_build_status" in names:
        return ("tool", "get_build_status", {"build_id": "b-1234"})
    if last["role"] == "tool":
        data = _text_of(last.get("content"))
        try:
            parsed = json.loads(data)
        except ValueError:
            return ("text", data)
        if isinstance(parsed, list):  # search_docs result
            if not parsed:
                return ("text", "I couldn't find this in the documents.")
            top = parsed[0]
            return ("text", f"Per {top['source']} (chunk {top['chunk_id']}): {top['text']}")
        if "error" in parsed:
            return ("text", f"The tool refused: {parsed['error']}")
        return ("text", f"Build {parsed['build_id']} is {parsed['status']}; failing step: {parsed['failing_step']}.")
    user = re.sub(r"<current_datetime>.*?</current_datetime>", "", _text_of(last.get("content")), flags=re.S).strip()
    m = re.search(r"\bb-\d+\b", user)
    if m and "get_build_status" in names:
        return ("tool", "get_build_status", {"build_id": m.group(0)})
    if "build" in user.lower() and "get_build_status" in names:
        return ("tool", "get_build_status", {"build_id": "not-an-id"})
    if "search_docs" in names:
        return ("tool", "search_docs", {"query": user})
    return ("text", "Typically 30 minutes.")  # confident, generic, unsourced


def completion(body):
    kind, *rest = decide(body)
    if kind == "tool":
        name, args = rest
        msg = {"role": "assistant", "content": None, "tool_calls": [
            {"id": f"call_{len(LOG)}", "type": "function",
             "function": {"name": name, "arguments": json.dumps(args)}}]}
        finish = "tool_calls"
    else:
        msg = {"role": "assistant", "content": rest[0]}
        finish = "stop"
    return msg, finish


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj):
        raw = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path.endswith("/models"):
            return self._send(200, {"object": "list", "data": [{"id": "mock-model", "object": "model"}]})
        self._send(404, {"error": "not found"})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        LOG.append(self.path)
        if not self.path.endswith("/chat/completions"):
            print("unhandled POST", self.path, file=sys.stderr)
            return self._send(404, {"error": "unsupported"})
        msg, finish = completion(body)
        base = {"id": "chatcmpl-mock", "object": "chat.completion", "created": int(time.time()), "model": "mock-model"}
        usage = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        if body.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.end_headers()
            delta = dict(msg)
            if "tool_calls" in delta:
                delta["tool_calls"] = [dict(tc, index=0) for tc in delta["tool_calls"]]
            chunks = [
                {**base, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": delta, "finish_reason": None}]},
                {**base, "object": "chat.completion.chunk", "choices": [{"index": 0, "delta": {}, "finish_reason": finish}], "usage": usage},
            ]
            for c in chunks:
                self.wfile.write(f"data: {json.dumps(c)}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")
            return
        self._send(200, {**base, "choices": [{"index": 0, "message": msg, "finish_reason": finish}], "usage": usage})


def serve(port=8765):
    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def use_offline():
    """Start the scripted server in a background thread and point the agent at it."""
    import os
    import threading
    threading.Thread(target=serve().serve_forever, daemon=True).start()
    os.environ["LAB_PROVIDER_URL"] = "http://127.0.0.1:8765/v1"
    os.environ["LAB_MODEL"] = "mock-model"
