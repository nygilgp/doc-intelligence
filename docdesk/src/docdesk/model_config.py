# docdesk/model_config.py
#
# NEW MODULE (see S2 E11 -- Model Selection and Tradeoffs)
#
# Centralizes model tier selection so the CHOICE is explicit and documented,
# not a hardcoded string repeated across classify.py, extract.py, tag_extract.py.
# Each task in docdesk gets a tier matched to its actual complexity/volume/
# latency needs -- not a default to "whatever is best."

# Verified current models (Sept 2026, platform.claude.com/docs/en/about-claude/pricing)
HAIKU = "claude-haiku-4-5"     # $1/$5 per MTok -- no adaptive thinking
SONNET = "claude-sonnet-5"     # $2/$10 per MTok -- adaptive thinking, 1M context
OPUS = "claude-opus-5"         # $5/$25 per MTok -- adaptive thinking, hardest reasoning

# Task -> tier mapping, with the REASONING documented inline.
# This is the artifact of E11's lesson: don't default to the biggest model.
TASK_MODEL_MAP = {
    # High-volume, narrow, fixed-category task. No adaptive reasoning needed.
    # Haiku is the architecturally AND economically correct choice.
    "classify_ticket": HAIKU,

    # Structured field extraction -- narrow but slightly more varied input
    # shapes than classification. Sonnet is the default for most production
    # workloads; this doesn't need Opus-level reasoning.
    "extract_fields": SONNET,

    # Tag extraction from arbitrary, sometimes long documents -- moderate
    # complexity, benefits from Sonnet's larger context window and adaptive
    # thinking for judgment calls on ambiguous documents.
    "extract_tags": SONNET,

    # Reserved for future, genuinely hard multi-document reasoning or
    # agentic tool-use chains (S3+) -- the actual justified use of Opus.
    "complex_agentic_reasoning": OPUS,
}


def get_model_for_task(task_name: str) -> str:
    """Look up the correct model tier for a named docdesk task.

    Raises KeyError loudly rather than silently defaulting -- an unmapped
    task should force a deliberate tier decision, not fall back to Opus
    'to be safe' (the anti-pattern this episode names).
    """
    if task_name not in TASK_MODEL_MAP:
        raise KeyError(
            f"No model tier mapped for task {task_name!r}. "
            "Add an explicit, reasoned entry to TASK_MODEL_MAP -- "
            "don't default to the biggest model."
        )
    return TASK_MODEL_MAP[task_name]