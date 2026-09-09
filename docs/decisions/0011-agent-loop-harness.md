# 11. docdesk uses a bounded agent loop; Agent SDK is the production default

## Status

Accepted

## Context

Document Q&A is agent-shaped: which tools are needed depends on the question.
We need an agent loop. Two options: hand-rolled harness (raw Messages API) or
the Claude Agent SDK, which runs the same loop for us.

## Decision

- Ship a hand-rolled, BOUNDED loop in `agent.py` for teaching + fine control:
  it checks stop_reason for normal completion and enforces MAX_TURNS as a hard
  cap against runaway looping.
- For most production agents, prefer the Claude Agent SDK (`claude-agent-sdk`),
  which provides the loop, tool execution, permissions, and context management.
  Use its `max_turns` / cost limits as the brake.

## Consequences

- Every loop MUST be bounded (completion check + hard cap). Non-negotiable.
- Ambiguous tool outputs cause runaway loops; tools return explicit signals
  (e.g. 'NO_MATCHES') so emptiness isn't read as 'keep trying'.
- Migration note: the Agent SDK was formerly the 'Claude Code SDK' (renamed).
