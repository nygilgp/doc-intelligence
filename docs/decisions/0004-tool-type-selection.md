# ADR 0004: Tool type selection

## Context

The Document Intelligence app needs external capabilities. Two concrete cases:

- Inventory lookups, wanted by MULTIPLE Claude apps, maintained by the platform team.
- A one-off order-status lookup needed ONLY by the support feature.

## Decision

- Inventory lookups → MCP server (reused across apps, independently maintained).
- One-off order-status lookup → custom tool inside the support app.
- Prefer built-in tools when Anthropic already ships the capability (e.g., web search).
- Use a Skill when we need Claude to follow a repeatable _procedure_, not call a system.

## Rejected

- Hard-coding API logic into prompts (not reusable/maintainable).
- Pasting live data into context per request (stale + wastes context).
- Building an MCP server for a single-app one-off (over-engineering).

## Rule of thumb for this codebase

Reused across apps + independently maintained → MCP. One-off app logic → custom tool.
Repeatable procedure → Skill. Already shipped → built-in.
