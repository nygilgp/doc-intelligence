"""Structured extraction (schema design) for the Document Intelligence app.

Requests a defined JSON schema so downstream code gets a predictable shape.
(Validation / defensive parsing is deepened in S4 Output Handling.)
"""
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