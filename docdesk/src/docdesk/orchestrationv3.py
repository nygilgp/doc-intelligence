# orchestration.py (new step) — few-shot payment-terms extraction
from prompts import PAYMENT_TERMS_SYSTEM, build_payment_terms_messages
from client import DocDeskClient

client = DocDeskClient()

def extract_payment_terms(contract_text: str) -> str:
    msg = client.create(
        system=PAYMENT_TERMS_SYSTEM,                       # standing role + rule
        max_tokens=16,                                     # a short phrase
        messages=build_payment_terms_messages(contract_text),  # shots + real input
    )
    return msg.content[0].text.strip()