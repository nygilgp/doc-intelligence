"""hooks.py — deterministic guardrails for docdesk's agent.

Connects to: agent.py (called before any tool executes — a PreToolUse gate).
WHY: the model is probabilistic; a system-prompt 'never delete /legal/' is NOT
enforceable. This hook blocks BEFORE execution, deterministically, every time.
"""

PROTECTED_PREFIXES = ("/legal/",)


class ToolBlocked(Exception):
    """Raised to deterministically prevent a tool call."""


def pre_tool_use(tool_name: str, tool_input: dict) -> None:
    """Runs BEFORE a tool executes. Raise ToolBlocked to prevent it.
    This is the hand-rolled equivalent of a PreToolUse hook."""
    if tool_name == "delete_document":
        path = tool_input.get("path", "")
        if path.startswith(PROTECTED_PREFIXES):
            raise ToolBlocked(f"BLOCKED: deletion of protected path {path}")


def post_tool_use(tool_name: str, tool_input: dict, result: str) -> None:
    """Runs AFTER a tool executes. AUDIT ONLY — cannot undo the action."""
    if tool_name == "delete_document":
        print(f"[AUDIT] deleted {tool_input.get('path')} -> {result}")