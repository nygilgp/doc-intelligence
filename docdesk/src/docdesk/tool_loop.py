# docdesk/tool_loop.py  (updated: parallel + approval gate)
from concurrent.futures import ThreadPoolExecutor
import anthropic
from docdesk.tools import (
    TOOLS, TOOL_IMPLEMENTATIONS, SENSITIVE_TOOLS, human_approves,
)

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5"

def _run_tool(block) -> dict:
    """Execute one tool_use block, returning a tool_result dict.
    On failure, return an is_error result with an INSTRUCTIVE message."""
    result = {"type": "tool_result", "tool_use_id": block.id}
    # 1) Approval gate for destructive/sensitive tools (deterministic control).
    if block.name in SENSITIVE_TOOLS and not human_approves(block.name, block.input):
        result["content"] = "User DENIED this action. Do not retry it."
        result["is_error"] = True
        return result
    # 2) Resilient execution.
    try:
        fn = TOOL_IMPLEMENTATIONS[block.name]
        result["content"] = fn(**block.input)
    except Exception as e:
        result["content"] = f"{type(e).__name__}: {e}. Ask the user to retry."
        result["is_error"] = True
    return result

def run(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    with ThreadPoolExecutor(max_workers=4) as pool:
        while True:
            resp = client.messages.create(
                model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages,
            )
            if resp.stop_reason != "tool_use":
                return "".join(b.text for b in resp.content if b.type == "text")
            messages.append({"role": "assistant", "content": resp.content})
            uses = [b for b in resp.content if b.type == "tool_use"]
            # 3) Independent tools run in parallel; results matched by tool_use_id.
            tool_results = list(pool.map(_run_tool, uses))
            messages.append({"role": "user", "content": tool_results})

if __name__ == "__main__":
    print(run("What's the total value of warehouse B?"))
