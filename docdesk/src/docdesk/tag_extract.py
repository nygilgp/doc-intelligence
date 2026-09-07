# docdesk/tag_extract.py
#
# NEW MODULE (see S2 E7 -- Prompting Techniques)
#
# This task (extracting short, lowercase, JSON-array tags from free-form
# documents) is format-sensitive: zero-shot instructions alone tend to
# produce inconsistent casing, tag length, or malformed JSON. Rather than
# escalating instruction intensity (the "instructing harder instead of
# showing" anti-pattern), we anchor the exact format with MULTI-SHOT
# examples covering a short doc, a long doc, and an ambiguous edge case.

import json
import anthropic
from docdesk.response_utils import get_text_block

client = anthropic.Anthropic()

# Three diverse examples -- chosen deliberately to cover different document
# shapes, not just repeated instances of the same easy case.
FEW_SHOT_EXAMPLES = """
Example 1:
Document: "Invoice #4521 is now 30 days overdue. Please remit payment for Q3 services."
Tags: ["invoice", "overdue", "q3"]

Example 2:
Document: "This quarterly report covers our expansion into the European market, 
including new hires in Berlin and Amsterdam, and a revised budget forecast for 
the remainder of the fiscal year."
Tags: ["quarterly-report", "expansion", "europe", "budget"]

Example 3 (ambiguous case -- short doc, few obvious keywords):
Document: "Please see attached."
Tags: ["attachment-reference"]
"""

SYSTEM_PROMPT = f"""Extract 2-5 relevant tags from the given document as a
JSON array of short, lowercase, hyphenated keyword strings. Follow the exact
format shown in these examples:
{FEW_SHOT_EXAMPLES}
Respond with ONLY the JSON array, no other text."""


def extract_tags(document_text: str) -> list[str]:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": document_text}],
    )
    raw = get_text_block(response).strip()

    # Defensive parsing -- never trust raw output blindly, even with
    # multi-shot anchoring the format.
    try:
        tags = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {raw!r}") from e

    if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
        raise ValueError(f"Expected a JSON array of strings, got: {tags!r}")

    return tags