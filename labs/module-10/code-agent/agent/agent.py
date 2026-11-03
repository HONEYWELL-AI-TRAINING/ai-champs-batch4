"""Build one agent session: instructions + tools + guardrails. `ask()` runs one question."""
import os
from dataclasses import dataclass, field

from copilot import CopilotClient

from .guards import Guard
from .rag import Index
from .tools import get_build_status, make_search_tool

BASE = (
    "You explain build failures for our engineers. Use tools; never guess. "
    "Say if unsure. Keep answers to three sentences."
)
GROUNDED = (
    " For questions about our procedures, limits, windows or contacts, call search_docs "
    "and answer ONLY from its results. Cite the source file and chunk id. "
    "If search_docs returns nothing relevant, say you could not find it in the documents."
)

# Lab 02, step 6: the fix for a "missed search" (the agent answers or asks instead of searching).
GROUNDED_STRICT = (
    " You have no knowledge of our services, systems or policies except what search_docs returns. "
    "For ANY question about our services, procedures, limits, windows, contacts or retention, ALWAYS call "
    "search_docs FIRST, even if you think you know. Answer ONLY from its results and cite the source file and "
    "chunk id. If search_docs returns nothing relevant, say you could not find it in the documents. "
    "Never ask a clarifying question instead of searching."
)

DEFAULT_MODEL = "gpt-5-mini"  # run `python check_setup.py` to see which models YOUR account can use


@dataclass
class Answer:
    text: str
    trace: list
    usage: dict = field(default_factory=lambda: {"model_calls": 0, "input_tokens": 0, "output_tokens": 0})


def _provider():
    url = os.environ.get("LAB_PROVIDER_URL")  # offline runs only; unset = your Copilot sign-in
    return {"type": "openai", "base_url": url, "api_key": "unused"} if url else None


async def ask(client, question, docs=None, max_tool_calls=4, timeout=90.0, strategy="section", strict=False):
    """docs=None -> ungrounded agent (Lab 01). docs='docs' -> retrieval tool + grounding instructions (Lab 02).
    strict=True uses the stronger GROUNDED_STRICT instructions (Lab 02, step 6)."""
    tools, instructions = [get_build_status], BASE
    if docs:
        tools.append(make_search_tool(Index.build(docs, strategy=strategy)))
        instructions += GROUNDED_STRICT if strict else GROUNDED
    guard = Guard([t.name for t in tools], max_tool_calls=max_tool_calls)
    kwargs = {"model": os.environ.get("LAB_MODEL", DEFAULT_MODEL)}
    if _provider():
        kwargs["provider"] = _provider()
    usage = {"model_calls": 0, "input_tokens": 0, "output_tokens": 0}

    def on_event(event):  # observe cost: one assistant.usage event per model call
        if getattr(event.type, "value", event.type) == "assistant.usage":
            usage["model_calls"] += 1
            usage["input_tokens"] += event.data.input_tokens or 0
            usage["output_tokens"] += event.data.output_tokens or 0

    async with await client.create_session(
        on_permission_request=guard.on_permission_request,
        tools=tools,
        available_tools=[t.name for t in tools],   # hides every built-in tool (shell, files, ...)
        system_message={"mode": "append", "content": instructions},
        hooks={"on_pre_tool_use": guard.pre_tool_use, "on_post_tool_use": guard.post_tool_use},
        on_event=on_event,
        **kwargs,
    ) as session:
        guard.session = session
        try:
            reply = await session.send_and_wait(question, timeout=timeout)
            text = reply.data.content if reply else "(no assistant message)"
            if guard.tripped:
                text = f"(stopped: step cap of {max_tool_calls} tool calls reached)"
        except Exception as exc:  # timeout, abort after the step cap, ...
            text = f"(stopped: {type(exc).__name__}: {exc})"
    return Answer(text, guard.trace, usage)


def new_client():
    return CopilotClient()
