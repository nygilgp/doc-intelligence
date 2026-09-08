# 8. Document processing uses a workflow, not an agent

## Status

Accepted

## Context

Document processing has a fixed shape: summarize -> classify -> store.
The path is fully knowable before runtime.

## Decision

Implement as a deterministic workflow in `orchestration.py`. Claude performs
the linguistic steps; our code owns the control flow.

## Consequences

- Predictable cost/latency (fixed call count), inspectable path, easy to test.
- If a future feature's path depends on runtime findings, revisit and escalate
  to the agent loop (planned S3 E4) — deliberately, not by default.
