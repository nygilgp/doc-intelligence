# 17. Summarizer sanitizes untrusted input and is refined via a regression harness

## Status

Accepted

## Context

docdesk summarizes end-user documents, which may contain prompt-injection text.
Raw interpolation let injected instructions sit flush with our instructions.
Prompt tweaks were being made ad hoc with no way to catch regressions.

## Decision

- Sanitize + isolate: wrap untrusted text in <document> tags in the USER turn,
  label it as data with a do-not-follow instruction, and neutralize literal
  closing tags (delimiter-escape). Pair with the PreToolUse delete guard.
- Iterative refinement: keep a regression harness (tests/test_prompts.py) that
  re-runs known-good cases + an injection attempt after every prompt change.

## Consequences

- Injection risk REDUCED (not eliminated) — guardrails remain the backstop.
- Prompt changes are made one at a time and verified, not blind-rewritten.
