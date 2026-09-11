# docdesk/tool_loop.py
"""Minimal tool-use loop. Runs beats 1-4 until Claude stops asking for tools."""
import anthropic
from docdesk.tools import TOOLS, TOOL_IMPLEMENTATIONS

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
MODEL = "claude-sonnet-5"       # pinned; see S1E22 on version pinning

def run(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]

    while True:
        resp = client.messages.create(
            model=MODEL, max_tokens=1024,
            tools=TOOLS, messages=messages,
        )

        if resp.stop_reason != "tool_use":
            # Beat 4: Claude is done — return its final text.
            return "".join(b.text for b in resp.content if b.type == "text")

        # Beat 2: gather every tool_use block Claude emitted.
        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            # Beat 3: run the REAL function and capture the result.
            fn = TOOL_IMPLEMENTATIONS[block.name]
            output = fn(**block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,   # <-- matches request to result
                "content": output,
            })
        messages.append({"role": "user", "content": tool_results})
        # Loop continues: Claude sees the results and answers (or calls again).

if __name__ == "__main__":
    print(run("What's the total value of warehouse B?"))