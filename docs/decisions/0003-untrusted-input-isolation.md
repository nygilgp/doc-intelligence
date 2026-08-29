# ADR 0003: Untrusted input isolation

## Context

The Document Intelligence app ingests user-uploaded documents and (later) retrieved
web content. Any of these can contain injected instructions (prompt injection).

## Decision

1. All user/retrieved content is treated as untrusted DATA.
2. It is structurally isolated from trusted instructions (wrapped/tagged, labeled as
   content to analyze, with an explicit instruction not to obey embedded commands).
3. Sensitive actions (email, DB access, deletions) are gated by deterministic
   guardrails/hooks (S6) under least privilege — untrusted text alone can never
   trigger them.

## Non-controls (explicitly rejected)

- Politely asking users not to inject (unenforceable).
- Raising temperature or upsizing the model (irrelevant / can worsen it).
- Relying on sanitization/filtering alone (brittle; supporting layer only).

## Rule of thumb for this codebase

Untrusted content is data, never instructions. Isolate + least privilege.
