"""
In-memory session store for the demo.

In production this would be Redis / Postgres / Firestore. For learning purposes
a process-local dict keeps the surface area small and the failure modes obvious.
"""

from dataclasses import dataclass, field
from threading import Lock
from time import time
from uuid import uuid4


@dataclass
class Session:
    sid: str
    persona_key: str
    strategy: str
    history: list[dict] = field(default_factory=list)
    created_at: float = field(default_factory=time)
    last_active: float = field(default_factory=time)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    turn_count: int = 0


class SessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = Lock()

    def create(self, persona_key: str, strategy: str, system_prompt: str) -> Session:
        sid = uuid4().hex[:12]
        sess = Session(
            sid=sid,
            persona_key=persona_key,
            strategy=strategy,
            history=[{"role": "system", "content": system_prompt}],
        )
        with self._lock:
            self._sessions[sid] = sess
        return sess

    def get(self, sid: str) -> Session | None:
        with self._lock:
            sess = self._sessions.get(sid)
            if sess is not None:
                sess.last_active = time()
            return sess

    def delete(self, sid: str) -> None:
        with self._lock:
            self._sessions.pop(sid, None)

    def list_active(self) -> list[Session]:
        with self._lock:
            return list(self._sessions.values())


# Module-level singleton — fine for a single-process dev server.
store = SessionStore()
