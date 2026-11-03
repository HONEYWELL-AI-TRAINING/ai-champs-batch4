"""Lab 04 — the smallest useful MCP server: one read-only tool.

Run it with the MCP Inspector:   uv run fastmcp dev server_minimal.py
"""
from fastmcp import FastMCP

mcp = FastMCP("Build Tools")


@mcp.tool
def get_build_status(build_id: str) -> dict:
    """Return the status and failing step of a CI build. Read-only.

    build_id looks like 'b-1234'.
    """
    if not build_id.startswith("b-"):
        raise ValueError("invalid build id: expected something like 'b-1234'")
    # Lab 04 stub. Lab 05 replaces this with the real data layer (data.py).
    return {"id": build_id, "status": "failed", "step": "unit-tests"}


if __name__ == "__main__":
    mcp.run()  # stdio by default
