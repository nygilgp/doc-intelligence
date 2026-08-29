# Decision Principles — Quick Reference

This project's core engineering judgments (see ADRs 0001–0006 for detail):

| Trigger                                                     | Reach for                               | ADR  |
| ----------------------------------------------------------- | --------------------------------------- | ---- |
| Overnight / bulk / non-urgent / cost-priority               | Message Batches API                     | 0001 |
| Match model to binding constraint (cost/latency/capability) | Haiku / Sonnet / Opus                   | 0002 |
| Untrusted input (uploaded/retrieved/user)                   | Isolate + least-privilege guardrails    | 0003 |
| Reusable across apps + independently maintained             | MCP server (one-off → custom tool)      | 0004 |
| Action must be blocked / require approval                   | Deterministic hook                      | 0005 |
| Output/behavior problem, unsure how heavy                   | Prompt → few-shot → context, then infra | 0006 |

Decoys that are usually wrong on security/enforcement questions:
temperature, model size, max_tokens, "ask more forcefully."
