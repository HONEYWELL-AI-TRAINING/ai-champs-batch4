"""
Minimal input / output guardrails for the demo.

For real production use, swap these for:
- OpenAI's Moderation API (`client.moderations.create(...)`)
- A dedicated PII detector (Presidio, Comprehend)
- A scope classifier fine-tuned for your domain
"""

import re

# Very small list — enough to demo the pattern, not an exhaustive policy
DENY_PATTERNS = [
    r"\bphishing\b",
    r"\bmalware\b",
    r"how (do|to) (i )?(make|build) (a |an )?(bomb|explosive|weapon)",
]

PII_PATTERNS = [
    (re.compile(r"\b\d{16}\b"),                     "[REDACTED-CARD]"),
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),          "[REDACTED-SSN]"),
    (re.compile(r"sk-(proj-)?[A-Za-z0-9-_]{20,}"),  "[REDACTED-APIKEY]"),
]


def check_input(text: str) -> dict:
    """
    Run cheap checks on the user message.

    Returns a dict:
      { "ok": bool, "reason": str | None, "redacted": str }
    """
    lower = text.lower()
    for pattern in DENY_PATTERNS:
        if re.search(pattern, lower):
            return {"ok": False, "reason": "unsafe", "redacted": text}

    redacted = text
    for pattern, replacement in PII_PATTERNS:
        redacted = pattern.sub(replacement, redacted)

    return {"ok": True, "reason": None, "redacted": redacted}


def check_output(text: str, system_prompt: str) -> dict:
    """
    Last-line-of-defence check on the model's reply.

    Catches obvious system-prompt leaks. Real chatbots also run moderation
    on the output and validate against domain rules.
    """
    # Heuristic: if a contiguous 60-char chunk of the system prompt appears
    # verbatim in the reply, treat it as a leak.
    if len(system_prompt) >= 60:
        sp_chunks = [system_prompt[i:i + 60] for i in range(0, len(system_prompt) - 60, 30)]
        for chunk in sp_chunks:
            if chunk.strip() and chunk.strip() in text:
                return {"ok": False, "reason": "system-prompt-leak"}
    return {"ok": True, "reason": None}


SAFE_DECLINE = (
    "I can't help with that. If you've got a question I can help with, "
    "I'd love to."
)
