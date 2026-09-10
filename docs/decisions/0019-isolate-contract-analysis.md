# 19. Contract analysis isolates separable concerns into fresh contexts

## Status

Accepted

## Context

Summary, key-dates, and risk are separable concerns needing different context.
A single-pass call kept the large risk rubric in context during the summary
(bloat) and let the three concerns interleave (drift), forcing us to prune/
compact a context that never needed to hold all three at once.

## Decision

Run three isolated steps, each a fresh focused context: summary (contract only),
dates (contract only), risk (contract + rubric — rubric enters only here). Heavy
risk work can be promoted to a subagent returning a compact finding.

## Consequences

- Each window holds only what its subtask needs: no bloat, no drift, sharper output.
- Isolation PREVENTS crowding; pruning/compaction remain for genuinely long
  single contexts.
- Cost: more calls than one pass — justified by separable, differently-scoped concerns.
