# 10. Complex document Q&A uses focused-subagent retrieval

## Status

Accepted

## Context

Answering complex questions over a large manual by stuffing all sections into
one context produced vague, conflated answers even when everything fit.

## Decision

Dispatch a focused subagent per relevant section (clean context, one section,
one job), returning a concise extract. The manager synthesizes from extracts
only — never the full sections.

## Consequences

- Sharper per-section extraction; no cross-section contamination.
- Chosen for QUALITY (focus), not only capacity — this holds even when the whole
  manual would fit in one window.
- Cost: more calls than a single-shot answer. Justified when answer quality on
  complex, multi-section questions matters. For a simple one-section question,
  a single call is the proportionate choice.
