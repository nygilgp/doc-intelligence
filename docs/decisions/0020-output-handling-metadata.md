# 20. Metadata extraction uses full output-handling discipline

## Status

Accepted

## Context

The prior extractor did json.loads(output) + data["key"], crashing on code
fences/preambles/missing keys and silently storing malformed or confidently-
wrong values. Model output is non-deterministic and must not be trusted blindly.

## Decision

Apply the full output-handling pipeline in extract.py::extract_meta:

- Structured output: explicit JSON shape in the instruction (a tool-use schema
  would enforce it more strongly — see S5).
- Defensive parsing: strip code fences/preamble, isolate the {...} block,
  try/except, return None on failure (flag for review, never crash).
- Validation: Pydantic schema enforces keys + types.
- Skepticism: plausibility check on value_usd (shape-valid != correct).

## Consequences

- Bad output is rejected/flagged, not stored or crashed on.
- Upgrade path: tool-use/function-calling for API-enforced structure (S5).
