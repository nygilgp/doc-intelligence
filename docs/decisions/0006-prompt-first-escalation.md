# ADR 0006: Prompt-first escalation policy

## Context

When output quality or behavior falls short, there's a wide range of possible fixes,
from editing a prompt to building new infrastructure. We need a default ordering so
we don't over-engineer.

## Decision

Default escalation order for any output/behavior problem:

1. Prompt / instruction fixes (clarity, output constraints).
2. Few-shot examples.
3. Context engineering (retrieval, structure).
4. Heavier machinery (custom tools, MCP, agent loops, fine-tuning) — only when 1–3
   are demonstrably insufficient, verified with evals.

## Exceptions (build machinery up front when the requirement demands it)

- Must-block/irreversible action → hook (ADR 0005).
- Capability reused across apps + independently maintained → MCP (ADR 0004).
- Latency-tolerant, high-volume job → batch (ADR 0001).

## Rule of thumb for this codebase

Start at the cheapest rung; escalate on evidence, not on instinct.
