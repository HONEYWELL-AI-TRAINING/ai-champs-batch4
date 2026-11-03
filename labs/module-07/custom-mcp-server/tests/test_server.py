"""Automated version of the Inspector checks: valid, invalid and missing input."""
import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

import data
from server import mcp


@pytest.fixture
async def client(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "DRAFTS_DIR", tmp_path / "drafts")
    async with Client(mcp) as c:
        yield c


async def test_lists_expected_tools(client):
    names = {t.name for t in await client.list_tools()}
    assert names == {"get_build_status", "list_recent_builds",
                     "get_test_failures", "draft_followup_issue"}


async def test_read_tools_are_marked_read_only(client):
    for t in await client.list_tools():
        expected = t.name != "draft_followup_issue"
        assert bool(t.annotations and t.annotations.readOnlyHint) is expected, t.name


async def test_get_build_status_valid(client):
    result = await client.call_tool("get_build_status", {"build_id": "b-1002"})
    assert result.data["status"] == "failed"
    assert result.data["failed_step"] == "unit-tests"


@pytest.mark.parametrize("bad", ["1002", "b-12", "b-1002; rm -rf /", "../etc/passwd"])
async def test_get_build_status_rejects_bad_id(client, bad):
    with pytest.raises(ToolError):
        await client.call_tool("get_build_status", {"build_id": bad})


async def test_get_build_status_missing_argument(client):
    with pytest.raises(ToolError):
        await client.call_tool("get_build_status", {})


async def test_unknown_build_gives_clear_message(client):
    with pytest.raises(ToolError, match="not found"):
        await client.call_tool("get_build_status", {"build_id": "b-9999"})


async def test_list_recent_builds_filters_and_limits(client):
    result = await client.call_tool("list_recent_builds", {"status": "failed", "limit": 1})
    # list results are wrapped by MCP as {"result": [...]}
    assert [b["status"] for b in result.structured_content["result"]] == ["failed"]
    with pytest.raises(ToolError):
        await client.call_tool("list_recent_builds", {"limit": 500})
    with pytest.raises(ToolError):
        await client.call_tool("list_recent_builds", {"status": "exploded"})


async def test_test_failures_output_is_capped(client, monkeypatch):
    monkeypatch.setitem(data.TEST_FAILURES, "b-1002",
                        [{"test": f"t{i}", "message": "x" * 5000} for i in range(50)])
    result = await client.call_tool("get_test_failures", {"build_id": "b-1002"})
    assert result.data["total_failures"] == 50
    assert len(result.data["failures"]) == 10
    assert all(len(f["message"]) <= 300 for f in result.data["failures"])


async def test_draft_followup_issue_writes_local_file_only(client):
    result = await client.call_tool("draft_followup_issue", {
        "build_id": "b-1002", "title": "Soft delete not persisted",
        "summary": "deleted_at is never set in unit tests."})
    assert result.data["posted"] is False
    assert (data.DRAFTS_DIR / "b-1002.md").read_text().startswith("# Soft delete")


async def test_runbook_resource_and_path_traversal(client):
    text = (await client.read_resource("docs://runbooks/flaky-tests"))[0].text
    assert "Re-run the failing job" in text
    for bad in ["..%2Fserver", "Flaky_Tests", "missing-runbook"]:
        with pytest.raises(Exception):
            await client.read_resource(f"docs://runbooks/{bad}")


async def test_prompt_is_listed_and_renders(client):
    assert "explain_build_failure" in {p.name for p in await client.list_prompts()}
    rendered = await client.get_prompt("explain_build_failure", {"build_id": "b-1002"})
    assert "b-1002" in rendered.messages[0].content.text
