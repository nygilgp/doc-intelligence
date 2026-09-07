# docdesk/streaming_demo.py
#
# DEMO MODULE (see S2 E9 -- Websockets & Streaming Transport)
#
# Demonstrates that Claude's streaming is ONE request -> ONE incrementally
# delivered response over a connection that then closes -- NOT a persistent,
# reusable, bidirectional channel like a websocket. A "follow-up" always
# requires a genuinely NEW, separate request.

import anthropic
from docdesk.response_utils import get_text_block

client = anthropic.Anthropic()


def stream_summary(document_text: str) -> str:
    """Streams a summary response. The stream is scoped to THIS ONE request
    only -- once it's done, the connection is closed. There is no mechanism
    to inject a new message into this same connection."""
    full_text = ""
    with client.messages.stream(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system="Summarize the document in 2-3 sentences.",
        messages=[{"role": "user", "content": document_text}],
    ) as stream:
        for chunk in stream.text_stream:
            full_text += chunk
            # In a real UI, you'd yield/display each chunk as it arrives here.
        # stream.get_final_message() available after the loop if you need
        # the full structured response object, not just the text.
    return full_text
    # <- connection is closed here. This function has returned. There is no
    #    open channel left to send a follow-up into.


def ask_followup(prior_document: str, prior_summary: str, followup_question: str) -> str:
    """A follow-up is a GENUINELY NEW, separate request -- not a continuation
    of the previous stream's connection. We pass prior context explicitly
    via message history, since the two requests share no underlying
    connection at all."""
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        system="Answer the follow-up question about the document, using the prior summary as context.",
        messages=[
            {"role": "user", "content": f"Document: {prior_document}"},
            {"role": "assistant", "content": prior_summary},
            {"role": "user", "content": followup_question},
        ],
    )
    return get_text_block(response)