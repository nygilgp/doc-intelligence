"""Structured extraction (schema design) for the Document Intelligence app.

Requests a defined JSON schema so downstream code gets a predictable shape.
(Validation / defensive parsing is deepened in S4 Output Handling.)
"""
# docdesk/extract.py
#
# NOTE ON DETERMINISM (see docs/decisions/ for ADR context):
# Claude generates output via next-token probabilistic prediction. This means
# free-text fields (summaries, explanations) may vary slightly between identical
# calls — that's expected, not a bug. This module exists specifically to pull
# fixed, structured fields (dates, IDs, amounts) OUT of free text and into a
# validated schema, precisely because we cannot and should not rely on prose
# stability for anything downstream systems depend on exactly matching.
#
# Full non-determinism controls (and their limits) are covered in S2 E5.

import json
from .client import _client, DEFAULT_MODEL, SYSTEM_PROMPT, extract_text, build_user_content

INVOICE_SCHEMA_INSTRUCTION = (
    'Return ONLY a JSON object, no prose, matching exactly:\n'
    '{"vendor": string, "total": number, "due_date": "YYYY-MM-DD"}'
)

def extract_invoice(document: str) -> dict:
    """Extract invoice fields as a structured dict via a requested JSON schema."""
    resp = _client.messages.create(
        model=DEFAULT_MODEL, max_tokens=512,
        system=SYSTEM_PROMPT + "\n" + INVOICE_SCHEMA_INSTRUCTION,
        messages=[{"role": "user", "content": build_user_content("Extract the fields.", document)}],
    )
    # Minimal parse now; robust defensive parsing arrives in S4.
    return json.loads(extract_text(resp))