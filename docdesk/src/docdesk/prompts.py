"""prompts.py (extended) — few-shot payment-terms extraction.

Connects to: orchestration.py (a new extraction step) + client.py.
WHY few-shot: 'payment terms as a short standardized phrase' is easy to SHOW,
hard to DESCRIBE. Three consistent examples (incl. a 'due on receipt' edge case)
pin the format. WHY placement: role + standing output constraint live in SYSTEM
(durable); each contract's text goes in USER (per-request, untrusted).
"""

PAYMENT_TERMS_SYSTEM = (
    "You are a contract analyst. Extract the payment terms as a short, "
    "standardized phrase (e.g. 'Net 30', 'Due on receipt'). "
    "Respond with ONLY the phrase, nothing else."
)

# Few-shot exemplars: alternating user(input) / assistant(desired output).
PAYMENT_TERMS_SHOTS = [
    {"role": "user", "content": "Payment shall be made within 30 days of invoice date."},
    {"role": "assistant", "content": "Net 30"},
    {"role": "user", "content": "The full amount is due immediately upon receipt."},
    {"role": "assistant", "content": "Due on receipt"},
    {"role": "user", "content": "Buyer shall remit payment no later than 60 days after delivery."},
    {"role": "assistant", "content": "Net 60"},
]


def build_payment_terms_messages(contract_text: str) -> list[dict]:
    """Few-shot messages: the exemplars, then the real contract as the final user turn."""
    return PAYMENT_TERMS_SHOTS + [{"role": "user", "content": contract_text}]