"""Tests that pin behavior across refactors — the safety net for S1 E18."""
from docdesk.client import build_user_content


def test_document_is_isolated_in_tags():
    """Untrusted documents must be wrapped in <document> tags (ADR 0003)."""
    out = build_user_content("What is the refund window?", "Refunds within 30 days.")
    assert out == "<document>\nRefunds within 30 days.\n</document>\n\nWhat is the refund window?"


def test_no_document_returns_plain_question():
    out = build_user_content("Hello", None)
    assert out == "Hello"