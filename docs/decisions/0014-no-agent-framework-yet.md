# 14. docdesk stays on the Claude Agent SDK; no agentic framework yet

## Status

Accepted

## Context

docdesk's agent is a single bounded loop with a handful of tools, memory, and
hooks. There is no complex multi-actor graph orchestration to coordinate.

## Decision

Stay on the Claude Agent SDK (and the bounded raw loop for teaching). Revisit a
framework only if a real need appears: PydanticAI for enforced typed I/O,
LangGraph for complex stateful multi-actor orchestration with crash-resume,
Strands for a lightweight AWS-centric build.

## Consequences

- Avoids framework-first over-engineering.
- The escalation trigger is a documented, specific need — not prestige.
