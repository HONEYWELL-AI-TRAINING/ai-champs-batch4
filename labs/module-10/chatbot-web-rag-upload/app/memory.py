"""
Memory strategies for the web chatbot.

Each strategy takes the full history and returns the messages array that
should be sent to the LLM on this turn.
"""

from typing import Literal

Strategy = Literal["full", "sliding", "summary"]


def apply_strategy(
    history: list[dict],
    strategy: Strategy,
    window_pairs: int = 4,
) -> list[dict]:
    """
    Trim history according to the selected strategy.

    Always preserves messages with role 'system'. For the 'summary' strategy
    we expect callers to have already injected an updated summary message
    (rotation happens elsewhere); here we just window the verbatim tail.
    """
    if strategy == "full":
        return history

    system = [m for m in history if m["role"] == "system"]
    rest = [m for m in history if m["role"] != "system"]

    if strategy == "sliding":
        keep = window_pairs * 2
        rest = rest[-keep:] if len(rest) > keep else rest
        return system + rest

    if strategy == "summary":
        # Keep system + last N messages verbatim. The summary itself is a
        # system message inserted by the rotate_summary() function.
        keep = window_pairs * 2
        rest = rest[-keep:] if len(rest) > keep else rest
        return system + rest

    return history


def should_rotate_summary(
    history: list[dict],
    summarize_every_turns: int,
) -> bool:
    """True if it's time to fold older turns into a summary message."""
    non_system = [m for m in history if m["role"] != "system"]
    pairs = len(non_system) // 2
    return pairs > 0 and pairs % summarize_every_turns == 0


def estimate_tokens(text: str) -> int:
    """Cheap heuristic — 1 token ≈ 0.75 words. Good enough for budgeting."""
    return int(len(text.split()) * 1.33)


def messages_token_estimate(messages: list[dict]) -> int:
    total = 0
    for m in messages:
        content = m.get("content", "")
        if isinstance(content, str):
            total += estimate_tokens(content) + 4  # role overhead
    return total
