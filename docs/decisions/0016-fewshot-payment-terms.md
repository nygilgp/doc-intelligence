# 16. Payment-terms extraction uses few-shot with system/user placement

## Status

Accepted

## Context

Payment-term phrasing varies wildly across contracts. A zero-shot instruction
produced inconsistent output shapes (prose vs. short phrase). The standardized
short-phrase format is easier to SHOW than to describe.

## Decision

Use few-shot: 3 consistent input->output exemplars (incl. a 'due on receipt'
edge case) as alternating user/assistant turns, then the real contract as the
final user turn. Put the durable role + output constraint in the SYSTEM
parameter; the per-request contract text goes in a USER turn.

## Consequences

- Consistent short-phrase output without fine-tuning or heavier machinery.
- System/user split keeps trusted rules separate from untrusted contract text
  (a security boundary deepened in S4 E3 / S6).
- Exemplars are versioned in prompts.py for review.
