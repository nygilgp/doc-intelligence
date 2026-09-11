# docdesk/tool_loop.py  (updated execution block)
import anthropic
from docdesk.tools import TOOLS, TOOL_IMPLEMENTATIONS

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5"

def _run_tool(block) -> dict:
    """Execute one tool_use block, returning a tool_result dict.
    On failure, return an is_error result with an INSTRUCTIVE message."""
    result = {"type": "tool_result", "tool_use_id": block.id}
    try:
        fn = TOOL_IMPLEMENTATIONS[block.name]
    except KeyError:
        result["content"] = (f"Unknown tool '{block.name}'. "
                             f"Do not call it again.")
        result["is_error"] = True
        return result
    try:
        result["content"] = fn(**block.input)
    except TypeError as e:
        # Bad/missing arguments → tell Claude what the tool needs.
        result["content"] = (f"Invalid arguments for {block.name}: {e}. "
                            f"Check the required fields and retry.")
        result["is_error"] = True
    except Exception as e:
        # Real execution failure → hand it back as recoverable info.
        result["content"] = (f"{type(e).__name__}: {e}. "
                            f"The service may be down; ask the user to retry.")
        result["is_error"] = True
    return result

def run(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    while True:
        resp = client.messages.create(
            model=MODEL, max_tokens=1024, tools=TOOLS, messages=messages,
        )
        if resp.stop_reason != "tool_use":
            return "".join(b.text for b in resp.content if b.type == "text")
        messages.append({"role": "assistant", "content": resp.content})
        tool_results = [_run_tool(b) for b in resp.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": tool_results})
        # Loop continues: Claude sees the results and answers (or calls again).

if __name__ == "__main__":
    print(run("What's the total value of warehouse B?"))
    
#python -c "from docdesk.tool_loop import run; print(run('Show open tickets for customer CUST-99999'))"
# The fake DB has no CUST-99999 → tool returns an ERROR string →
# Claude replies: "I couldn't find a customer with ID CUST-99999 — please double-check it."