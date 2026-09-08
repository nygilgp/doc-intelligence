# docdesk/document_qa.py
#
# NEW MODULE (see S2 E12 -- Cost and Token Management)
#
# The reference document is the dominant cost driver here: it's sent as
# context on EVERY question in a session. We cache it explicitly via
# cache_control so only the FIRST question in a session pays full price
# for the document; every subsequent question reads it at 0.1x input price.
#
# We use the default 5-minute cache (not the extended 1-hour option) because
# a typical user Q&A session is short -- the break-even is just 1 read, and
# most sessions will have several questions within a 5-minute window.
#
# NOTE: "ephemeral" is currently the ONLY cache_control type -- there isn't a
# second type to choose between. What varies is the optional `ttl` field
# inside it: "5m" (default, omit ttl entirely) or "1h" (2x write cost instead
# of 1.25x, but a longer window -- worth it if response generation time is
# eating into the 5-minute clock, since the TTL starts at request start, not
# response end, and up to 4 cache breakpoints are allowed per request). We're
# using the 5m default here, so ttl is simply omitted.

import anthropic
from docdesk.model_config import get_model_for_task
from docdesk.response_utils import get_text_block

client = anthropic.Anthropic()


def ask_about_document(document_text: str, question: str) -> str:
    """Ask a question about a document, with the document cached so
    repeated questions in the same session don't re-pay full input price
    for identical content."""
    response = client.messages.create(
        model=get_model_for_task("extract_fields"),  # Sonnet 5 -- see model_config.py
        max_tokens=500,
        system=[
            {
                "type": "text",
                "text": "Answer questions about the following document accurately and concisely.",
            },
            {
                "type": "text",
                "text": document_text,
                # Marks the document as cacheable. First call: write cost
                # (1.25x, since ttl is omitted -> defaults to 5m). Every call
                # within 5 minutes reusing this EXACT content: read cost
                # (0.1x) instead of full price.
                "cache_control": {"type": "ephemeral"},
            },
        ],
        messages=[{"role": "user", "content": question}],
    )

    # Real cost visibility -- inspect usage to confirm caching is actually
    # working, rather than assuming it silently.
    usage = response.usage
    print(
        f"[cost] input={usage.input_tokens} "
        f"cache_write={getattr(usage, 'cache_creation_input_tokens', 0)} "
        f"cache_read={getattr(usage, 'cache_read_input_tokens', 0)} "
        f"output={usage.output_tokens}"
    )

    return get_text_block(response)


def ask_about_document_long_session(document_text: str, question: str) -> str:
    """Variant for longer-running sessions (e.g. an agent workflow that may
    pause for minutes between questions, or where response generation is
    slow enough to eat meaningfully into a 5-minute window). Uses the
    extended 1-hour TTL -- 2x write cost instead of 1.25x, but the cache
    survives a much longer gap between requests."""
    response = client.messages.create(
        model=get_model_for_task("extract_fields"),
        max_tokens=500,
        system=[
            {
                "type": "text",
                "text": "Answer questions about the following document accurately and concisely.",
            },
            {
                "type": "text",
                "text": document_text,
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            },
        ],
        messages=[{"role": "user", "content": question}],
    )
    return get_text_block(response)