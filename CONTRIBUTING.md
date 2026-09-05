# Contributing to the Document Intelligence & Support Application

## Workflow (applies to ALL code, including AI-generated)

1. Create a branch: `git checkout -b feature/<name>`
2. Make changes; commit with a clear message.
3. Add/run tests — required for any destructive or data-changing operation.
4. Open a Pull Request. A human reviews the diff before merge.
5. Merge to `main` only after review passes.

## AI-generated code

Code produced by Claude/Claude Code is an INPUT to this process, not an exception
to it. It is branched, tested, and PR-reviewed like any other change. Reviewers
check for: hallucinated/incorrect APIs, missing edge cases, and insecure patterns.
Plausible-looking is not the same as correct.

## Decisions

Significant choices are recorded as ADRs in docs/decisions/ (see 0001–0006).
