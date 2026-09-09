"""agent.py — a bounded, hand-rolled agent loop (harness) for docdesk.

Connects to: client.py (the Claude client). Tools are stubbed here; S5 wires in
real document-search / file-read / record-lookup tools.

WHY hand-rolled here: this episode teaches the loop mechanism explicitly. In
production you'd often use the Claude Agent SDK (see ADR 0011) — it runs this
same loop for you. We keep the raw version so the send->tool->repeat cycle and
the two stop conditions (end_turn + hard cap) are visible and testable.
"""
from client import DocDeskClient

# agent.py (updated _dispatch) — PreToolUse gate + PostToolUse audit
from hooks import pre_tool_use, post_tool_use, ToolBlocked

client = DocDeskClient()
MODEL = "claude-sonnet-5"          # pinned; see api-corrections on model pinning
MAX_TURNS = 8                       # THE BRAKES — hard cap against runaway loops

# Tool schemas Claude is allowed to request (implementations stubbed for now).
TOOLS = [
    {
        "name": "search_documents",
        "description": "Search the document library for relevant files. "
                       "Returns matching doc IDs, or an explicit 'NO_MATCHES' "
                       "so the model does not mistake emptiness for 'try again'.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    # read_file, lookup_record ... added in S5
]

def _dispatch(tool_name: str, tool_input: dict) -> str:
    try:
        pre_tool_use(tool_name, tool_input)      # deterministic gate — may block
    except ToolBlocked as e:
        return str(e)                            # tool never runs; tell the model

    # ... run the actual tool ...
    result = "NO_MATCHES" if tool_name == "search_documents" else "OK"

    post_tool_use(tool_name, tool_input, result)  # audit only, after the fact
    return result

# The managed-loop equivalent: a PreToolUse callback on options.hooks.
# from claude_agent_sdk import query, ClaudeAgentOptions

# async def block_legal_deletes(input, tool_use_id, context):
#     if input["tool_name"] == "delete_document" and \
#        input["tool_input"].get("path", "").startswith("/legal/"):
#         return {"decision": "block", "reason": "protected /legal/ path"}
#     return {}

# options = ClaudeAgentOptions(
#     hooks={"PreToolUse": [block_legal_deletes]},   # fires before every tool
#     max_turns=8,
# )


def run_agent(user_question: str) -> str:
    """The agent loop. Two stop conditions:
       (1) normal: stop_reason != 'tool_use' (Claude is done)
       (2) safety: MAX_TURNS reached (the deterministic brake)."""
    messages = [{"role": "user", "content": user_question}]

    for turn in range(MAX_TURNS):
        resp = client.create(model=MODEL, max_tokens=1024,
                             messages=messages, tools=TOOLS)
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            # end_turn (or any non-tool stop) => Claude has finished
            return "".join(b.text for b in resp.content if b.type == "text")

        # Claude requested one or more tools — run each, feed results back.
        tool_results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = _dispatch(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
        messages.append({"role": "user", "content": tool_results})

    # Hit the cap without finishing — fail loud, don't loop forever.
    return "AGENT_STOPPED: reached MAX_TURNS without completing the task."


if __name__ == "__main__":
    print(run_agent("Which of my contracts mention a data-privacy clause?"))