# ADR 0005: Deterministic control via hooks

## Context

The agent can call tools including delete_document(id) and send_email(to, body).
Some actions are destructive/irreversible and MUST be guaranteed-safe, even under
prompt injection or model error.

## Decision

- delete_document on the `production` bucket → blocked by a deterministic pre-tool-use
  hook (code), not a system-prompt request.
- send_email → requires explicit human approval via a pre-tool-use hook.
- System-prompt wording may express intent, but is NEVER the enforcement mechanism
  for destructive/sensitive actions.

## Rejected

- Prompt-as-enforcement (relying on "never delete prod" in the system prompt).

## Rule of thumb for this codebase

If an action MUST be blocked or MUST require approval, enforce it with a hook.
Prompts request; hooks guarantee.
