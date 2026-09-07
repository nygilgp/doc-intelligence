# docdesk/classify.py
#
# NOTE ON TEMPERATURE / SAMPLING PARAMETERS (see S2 E4, E5 — and this correction):
# Earlier versions of this module set temperature=0 to bias the model toward its
# single highest-probability token for this narrow, single-correct-answer task.
#
# CORRECTION: On Claude models released after Opus 4.6 (i.e. 4.7 and later,
# including Sonnet 5 and Opus 5), the temperature/top_p/top_k sampling parameters
# are DEPRECATED. Sending a non-default value (like temperature=0) now returns a
# 400 error. Anthropic's guidance: omit the parameter entirely and use prompting
# / system instructions to guide behavior instead.
#
# The underlying LESSON from E4/E5 is still exam-relevant and still true:
#   - Narrow, single-correct-answer tasks (classification, extraction) want the
#     model to reliably commit to its best guess, not explore alternatives.
#   - Even at the old temperature=0, output was never a hard determinism
#     guarantee -- Anthropic's own docs confirmed this.
# What changed is HOW you express that intent: not a numeric dial anymore, but
# explicit, strict prompt instructions -- which is exactly what the "prompt-first"
# Season 0 meta-skill already pointed toward.

import anthropic
from docdesk.response_utils import get_text_block

client = anthropic.Anthropic()

CATEGORIES = ["billing", "technical", "account", "legal", "other"]

def classify_ticket(ticket_text: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=10,
        # NOTE: no `temperature` parameter sent. On Claude 4.7+ models this
        # would 400 if set to a non-default value. We rely entirely on strict
        # prompt instructions below to constrain the output to one exact word --
        # this IS the "prompt-first" approach, now the only approach.
        system=(
            "Classify the support ticket into exactly one category. "
            f"Respond with ONLY one of these exact words: {', '.join(CATEGORIES)}. "
            "No other text, no punctuation, no explanation -- the single word only."
        ),
        messages=[{"role": "user", "content": ticket_text}],
    )
    category = get_text_block(response).strip().lower()

    # Defensive parsing (S4/S8 territory) -- never trust raw output blindly,
    # this matters even more now that we can't lean on temperature at all.
    if category not in CATEGORIES:
        raise ValueError(f"Unexpected category returned: {category!r}")

    return category