"""The agent's tools: one read-only lookup (Lab 01) and retrieval (Lab 02).

Same tool-design rules as Module 07: one tool, one job; describe it for the model;
typed and validated inputs; small structured output; read-only.
"""
import json
import re

from pydantic import BaseModel, Field

from copilot import define_tool

# Stand-in for a CI API. Replace with a real read-only client.
BUILDS = {
    "b-1234": {"status": "failed", "failing_step": "unit-tests"},
    "b-1235": {"status": "passed", "failing_step": "none"},
}


class BuildParams(BaseModel):
    build_id: str = Field(description="Build id, looks like b-1234 (b- then four digits)")


@define_tool(
    description="Status and failing step for one build. Read-only. "
    "Use when the user asks why a build failed or passed. id looks like b-1234.",
    skip_permission=False,
)
async def get_build_status(params: BuildParams) -> str:
    if not re.fullmatch(r"b-\d{4}", params.build_id):  # re-check in the handler, never trust the model
        return json.dumps({"error": f"build_id must look like b-1234, got {params.build_id!r}"})
    build = BUILDS.get(params.build_id)
    if build is None:
        return json.dumps({"error": f"no build {params.build_id}"})
    return json.dumps({"build_id": params.build_id, **build})


class SearchParams(BaseModel):
    query: str = Field(description="What to look up in the runbooks, in plain words")
    k: int = Field(default=4, ge=1, le=8, description="How many passages to return")


def make_search_tool(index):
    """Retrieval is just another tool (deck slide 13)."""

    @define_tool(
        name="search_docs",
        description="Search the team runbooks and policies. Returns passages with source file "
        "and chunk id. Use for any question about our procedures, limits, windows or contacts. "
        "Returns [] when nothing relevant exists.",
    )
    async def search_docs(params: SearchParams) -> str:
        hits = index.search(params.query, k=params.k)
        return json.dumps([{k: h[k] for k in ("text", "source", "chunk_id")} for h in hits])

    return search_docs
