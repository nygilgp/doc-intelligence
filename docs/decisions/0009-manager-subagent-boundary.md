# 9. Contract review uses a manager/subagent context boundary

## Status

Accepted

## Context

Three separate rulebooks (financial, liability, privacy) are each large.
Loading all three into one agent's context bloats it and mixes specialties.

## Decision

A manager coordinator delegates each specialty to an isolated worker call that
sees ONLY its own rulebook + the contract. Workers return compact reports; the
manager synthesizes from reports alone.

## Consequences

- Each context window stays small and focused; specialties don't cross-contaminate.
- If a specialty needs runtime follow-up investigation, this coordinator is the
  natural place to escalate to a true agent loop (S3 E4).
- If the path never varies and no follow-up is needed, a plain workflow fan-out
  would suffice — revisit before adding loop machinery.
