# tests/test_classify.py
#
# NOTE ON TEST DESIGN (see S2 E5 — Non-Determinism):
# Even at temperature=0, LLM output is not guaranteed byte-identical across runs.
# We reserve strict exact-match assertions for UNAMBIGUOUS inputs, and use a
# rubric (a set of acceptable answers) for genuinely borderline inputs where
# more than one category could reasonably apply. This avoids "chasing a phantom
# regression" when a rare flake happens on an ambiguous case — while still
# catching real regressions on clear-cut cases.

from docdesk.classify import classify_ticket

def test_classify_unambiguous_billing_ticket():
    # Clearly a billing issue — no reasonable ambiguity. Safe to assert exactly.
    ticket = "I was charged twice for my subscription this month, please refund the duplicate charge."
    result = classify_ticket(ticket)
    assert result == "billing"

def test_classify_borderline_ticket_against_rubric():
    # This ticket plausibly touches "billing", "account", or "technical" categories.
    # We assert membership in an acceptable set, NOT a single exact string,
    # because this is a genuinely borderline case ("can't log in" reads as technical).
    ticket = "I can't log in to update my payment method on my account."
    acceptable = {"billing", "account", "technical"}
    result = classify_ticket(ticket)
    assert result in acceptable, (
        f"Got {result!r}, expected one of {acceptable}. "
        "If this fails repeatedly (not just once), investigate for a real regression."
    )