# ADR 0001: Batch vs Realtime routing

## Context

The Document Intelligence app has two workloads:

- Live support chat (user-facing, interactive)
- Nightly bulk re-analysis of the document archive (report due 9am)

## Decision

- Live support chat → synchronous Messages API (latency is the product).
- Nightly bulk re-analysis → Message Batches API (latency-tolerant, ~50% cheaper).

## Rule of thumb for this codebase

Route by latency tolerance, not by "which is cheaper" or "which is faster."
"Is someone waiting on this answer right now?" → Yes = realtime, No = batch.
