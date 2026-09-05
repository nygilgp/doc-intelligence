# ADR 0007: Content boundaries and interface assumptions

## Context

The app is built on the Anthropic API (and optionally Bedrock). The API is a blank
surface: no product system prompt, memory, or guardrails are supplied for us. Prompts
prototyped in claude.ai will NOT carry that product context here.

## Decision

1. We supply the FULL system prompt ourselves (SYSTEM_PROMPT in client.py). We rely on
   no product-level framing.
2. Content boundaries are explicit and structural:
   - Trusted instructions → `system` parameter only.
   - Untrusted user/document content → isolated in a tagged `user` turn via
     build_user_content() (<document>...</document>).
   - Multiple documents are separated with distinct labeled boundaries.
3. Because the API has no product guardrails, our isolation (ADR 0003) and future hooks
   (ADR 0005 / S6) are the ONLY protection — they are not optional.

## Rejected

- Assuming a claude.ai-tested prompt behaves identically on the API (interface-transfer
  assumption).

## Rule of thumb for this codebase

On the API, we own the entire instruction context. Boundaries are designed, not assumed.
