# ADR 0002: Model tier routing

## Context

The Document Intelligence app runs workloads with different demands:

- Document classification (simple, very high volume)
- Contract Q&A (hard, multi-clause reasoning)
- Acknowledgement replies (trivial, templated)

## Decision

- Classification → Haiku (fast, cheap, capable enough).
- Contract Q&A → Opus, pending eval check against Sonnet.
- Acknowledgement replies → Haiku.

## Rule of thumb for this codebase

Match the tier to the task's _binding constraint_ (capability / latency / cost).
Start at the smallest tier that plausibly meets the quality bar; move up only if
evals show a shortfall. Never default to the biggest model "to be safe."
