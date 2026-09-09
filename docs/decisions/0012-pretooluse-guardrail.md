# 12. /legal/ deletion is blocked by a PreToolUse guardrail, not a prompt

## Status

Accepted

## Context

The agent gains a delete_document tool. Compliance requires that files under
/legal/ are NEVER deletable. A system-prompt request is probabilistic and not
enforceable; PostToolUse logging fires after the fact and cannot prevent.

## Decision

Enforce with a PreToolUse-style gate (hooks.py::pre_tool_use, wired into
agent.py dispatch): it inspects the target path BEFORE execution and blocks
deletes under /legal/. Deterministic — fires identically every time. A
PostToolUse audit log records allowed deletes.

## Consequences

- Prevention is deterministic and independent of model behavior.
- Layered: PreToolUse prevents, PostToolUse observes.
- On the Agent SDK, the same rule is a PreToolUse callback on options.hooks
  returning {"decision": "block"}.
