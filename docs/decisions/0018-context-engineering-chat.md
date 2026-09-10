# 18. Document chat engineers its context (prune + compact)

## Status

Accepted

## Context

The chat path re-sent the full document + full history every turn, causing
bloat (re-billed tokens, latency) and drift (declining answer quality on long
chats). Blind truncation risked severing load-bearing facts.

## Decision

- PRUNE the document to the question-relevant slice (retrieval/selection),
  not the whole document.
- COMPACT distant turns into a running summary that PRESERVES established facts
  (names, dates, which document); keep the last KEEP_RECENT turns verbatim.
- Reuse the <document> delimiter from S4 E3 for the pruned slice (still untrusted).

## Consequences

- Leaner window: lower cost + latency, sharper answers on long conversations.
- Selective (not blind) reduction avoids losing load-bearing context.
- Complements S3 E6's memory tool for cross-session durability.
