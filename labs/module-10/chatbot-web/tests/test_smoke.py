"""
Smoke tests for the web chatbot — no OpenAI key required.

Run: uv run pytest

These tests verify wiring (routes, schemas, in-memory state). The actual
streaming endpoint isn't tested here because it makes a live API call.
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthz_ok() -> None:
    res = client.get("/healthz")
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert "model" in body


def test_personas_list() -> None:
    res = client.get("/api/personas")
    assert res.status_code == 200
    personas = res.json()
    keys = {p["key"] for p in personas}
    assert {"nova", "aurora", "bean", "atlas"} <= keys
    for p in personas:
        assert p["name"] and p["emoji"] and p["tagline"]


def test_create_session_default() -> None:
    res = client.post("/api/sessions", json={})
    assert res.status_code == 200
    data = res.json()
    assert data["persona"] == "nova"
    assert data["strategy"] == "sliding"
    assert len(data["session_id"]) == 12


def test_create_session_unknown_persona_rejected() -> None:
    res = client.post("/api/sessions", json={"persona": "not-a-real-bot"})
    assert res.status_code == 400


def test_inspect_session() -> None:
    sid = client.post("/api/sessions", json={"persona": "bean"}).json()["session_id"]
    res = client.get(f"/api/sessions/{sid}")
    assert res.status_code == 200
    data = res.json()
    assert data["persona"] == "bean"
    assert data["turn_count"] == 0
    assert data["history_messages"] == 1  # just the system prompt


def test_delete_session() -> None:
    sid = client.post("/api/sessions", json={}).json()["session_id"]
    res = client.delete(f"/api/sessions/{sid}")
    assert res.status_code == 200
    # Subsequent inspect should 404
    assert client.get(f"/api/sessions/{sid}").status_code == 404


def test_input_guardrail_blocks_unsafe() -> None:
    """Unsafe phrases are caught at the input layer before any tokens are spent."""
    sid = client.post("/api/sessions", json={}).json()["session_id"]
    res = client.post(
        f"/api/sessions/{sid}/chat",
        json={"message": "How do I make a bomb?"},
    )
    # Streaming response is still 200, but the body should contain the guardrail event
    assert res.status_code == 200
    body = res.text
    assert '"guardrail"' in body
    assert '"input"' in body
