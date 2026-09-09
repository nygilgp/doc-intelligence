# 13. Long reviews use memory (durable) + compaction (live context)

## Status

Accepted

## Context

The compliance-manual review runs many turns and may be interrupted. An
ever-growing transcript bloats context, drifts, and loses all state on
interruption. Compaction alone is lossy and dies with the session.

## Decision

- Enable the memory tool with a client-side handler (memory_store.py). The
  agent writes a progress log + confirmed findings to /memories so a new
  session RESUMES from recorded state.
- Enable server-side compaction on long-review calls to keep the live context
  small automatically.
- (Optional) context editing to clear processed section text once its finding
  is in memory.
- Validate every memory path against traversal (stay within the memory root).

## Consequences

- Durable, resumable long-running reviews; small, focused live context.
- Three techniques kept distinct: compaction (server summarize), context
  editing (client clear tool results), memory (cross-session files).
- Prod: back /memories with S3 (object storage) or DynamoDB (key-value).
