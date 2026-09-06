# Document Intelligence & Support Application — Project Context

## Architecture

- src/docdesk/client.py — vendor-flexible Claude client (Anthropic / Bedrock).
- errors.py — error classification + backoff retry. batch.py — batch lane.
- concurrent.py — async concurrent lane. session.py — bounded sessions.
- Decisions recorded as ADRs in docs/decisions/.

## Conventions

- Untrusted content is isolated in tagged user turns (ADR 0003 / 0007). Never in system.
- Model versions are PINNED in config.py; prompts are VERSIONED. No floating "latest".
- All code (incl. AI-generated) is branched, tested, and PR-reviewed (CONTRIBUTING.md).
- Destructive actions must be gated by hooks (ADR 0005), not prompt requests.
