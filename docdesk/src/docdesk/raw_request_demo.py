# docdesk/raw_request_demo.py
#
# DEMO MODULE (see S2 E8 -- SDKs That Wrap REST APIs)
#
# This module makes the SAME classify_ticket() request as classify.py --
# but via raw HTTP instead of the SDK, to make concrete that the SDK is a
# convenience wrapper around a standard REST endpoint, not a different API.
# NOT meant for production use in docdesk -- classify.py (SDK-based) remains
# the real implementation. This exists purely to demonstrate the underlying
# mechanism for this episode.

import os
import json
import httpx  # same HTTP library the SDK itself uses under the hood

API_URL = "https://api.anthropic.com/v1/messages"


def classify_ticket_raw_http(ticket_text: str) -> str:
    headers = {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": "claude-sonnet-4-5",
        "max_tokens": 10,
        "system": (
            "Classify the support ticket into exactly one category. "
            "Respond with ONLY one of these exact words: billing, technical, "
            "account, legal, other. No other text."
        ),
        "messages": [{"role": "user", "content": ticket_text}],
    }

    response = httpx.post(API_URL, headers=headers, json=body, timeout=30.0)
    response.raise_for_status()  # SDK would do structured error classification here (S1 E7-E8)
    data = response.json()

    # This is exactly what get_text_block() does for you via the SDK's typed
    # response object -- here we're doing it by hand against raw JSON.
    text_block = next(
        (block for block in data["content"] if block["type"] == "text"), None
    )
    return text_block["text"].strip().lower()