"""The agent end to end through the real Copilot SDK + runtime, against the scripted model."""
import json

import pytest

import mock_model
from agent.agent import ask, new_client


@pytest.fixture
async def client():
    async with new_client() as c:
        yield c


async def test_one_tool_agent_answers_from_the_tool(client):
    a = await ask(client, "Why did build b-1234 fail?")
    assert "unit-tests" in a.text
    assert [t["tool"] for t in a.trace] == ["get_build_status"]
    assert a.trace[0]["decision"] == "allow" and a.trace[0]["result_chars"] > 0


async def test_bad_arguments_are_rejected_inside_the_tool(client):
    a = await ask(client, "Why did the build fail?")        # scripted model passes id "not-an-id"
    assert "refused" in a.text.lower() or "must look like" in a.text


async def test_ungrounded_agent_gives_a_confident_unsourced_answer(client):
    a = await ask(client, "What is our rollback window for the payments service?")
    assert "Typically 30 minutes" in a.text and a.trace == []   # the baseline failure the lab shows


async def test_grounded_agent_cites_its_source(client):
    a = await ask(client, "What is our rollback window for the payments service?", docs="docs")
    assert "runbook-payments.md" in a.text and "45 minutes" in a.text
    assert any(t["tool"] == "search_docs" for t in a.trace)


async def test_grounded_agent_declines_when_docs_cannot_answer(client):
    a = await ask(client, "What is the refund approval limit?", docs="docs")
    assert "couldn't find" in a.text.lower()


async def test_allow_list_hides_built_in_tools(client):
    mock_model.TOOLS_SEEN.clear()
    await ask(client, "Why did build b-1234 fail?")
    offered = {n for seen in mock_model.TOOLS_SEEN for n in seen}
    assert offered == {"get_build_status"}                      # no shell, no file tools


async def test_runaway_loop_is_stopped_by_the_step_cap(client):
    mock_model.LOOP_FOREVER = True
    try:
        a = await ask(client, "Why did build b-1234 fail?", max_tool_calls=3, timeout=30)
    finally:
        mock_model.LOOP_FOREVER = False
    assert "step cap" in a.text
    assert sum(1 for t in a.trace if t["decision"] == "allow") == 3
    assert any(t["decision"] == "deny: step cap" for t in a.trace)


async def test_usage_events_are_counted(client):
    a = await ask(client, "Why did build b-1234 fail?")
    assert a.usage["model_calls"] >= 2                           # tool call turn + answer turn


async def test_strict_instructions_still_ground_and_cite(client):
    a = await ask(client, "How long do we keep incident logs?", docs="docs", strict=True)
    assert "incident-policy.md" in a.text and any(t["tool"] == "search_docs" for t in a.trace)
