"""Controls around the loop (deck slide 9): allow-list, permission handler, step cap, trace."""
import asyncio

from copilot.rpc import PermissionDecisionApproveOnce, PermissionDecisionReject
from copilot.session_events import PermissionRequestCustomTool


class Guard:
    def __init__(self, allowed, max_tool_calls=4):
        self.allowed = set(allowed)
        self.max_tool_calls = max_tool_calls
        self.trace = []          # one dict per tool call: tool, args, decision, result size
        self.session = None      # set after create_session so we can abort a runaway
        self.tripped = False

    # BEFORE a tool call: allow, deny, or stop the run.
    async def pre_tool_use(self, hook_input, invocation):
        name, args = hook_input["toolName"], hook_input.get("toolArgs")
        entry = {"tool": name, "args": args, "decision": "allow"}
        if name not in self.allowed:
            entry["decision"] = "deny: not on allow-list"
        elif sum(1 for t in self.trace if t["decision"] == "allow") >= self.max_tool_calls:
            entry["decision"] = "deny: step cap"
            self.tripped = True
        self.trace.append(entry)
        if entry["decision"] == "allow":
            return {"permissionDecision": "allow"}
        if self.tripped and self.session is not None:
            # Schedule the abort so this hook can return first; awaiting it here
            # makes send_and_wait sit out its full timeout.
            asyncio.get_running_loop().create_task(self.session.abort())
        return {"permissionDecision": "deny", "permissionDecisionReason": entry["decision"]}

    # AFTER a tool call: record how big the result was (log the size, don't dump the content).
    async def post_tool_use(self, hook_input, invocation):
        for entry in reversed(self.trace):
            if entry["tool"] == hook_input["toolName"] and "result_chars" not in entry:
                entry["result_chars"] = len(str(hook_input.get("toolResult")))
                break

    # PERMISSION handler: only our own custom tools, only by name.
    def on_permission_request(self, request, invocation):
        if isinstance(request, PermissionRequestCustomTool) and request.tool_name in self.allowed:
            return PermissionDecisionApproveOnce()
        return PermissionDecisionReject(feedback="Not permitted for this agent")
