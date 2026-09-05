"""Raw HTTP reference: calling Claude with no SDK, just HTTP + JSON.

Not the primary path (client.py's SDK is better), but this documents the exact
wire format the SDK produces, for teammates on stacks without an Anthropic SDK.
"""
import os
import json
import httpx

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"   # the REST resource


def ask_raw(question: str, max_tokens: int = 1024) -> str:
    """POST /v1/messages by hand: JSON body, auth + version headers, parse JSON back."""
    headers = {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],   # auth
        "anthropic-version": "2023-06-01",              # API version header
        "content-type": "application/json",             # body IS json
    }
    body = {                                            # a plain dict → serialized to JSON
        "model": "claude-sonnet-4-5",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": question}],
    }

    resp = httpx.post(ANTHROPIC_URL, headers=headers, json=body)  # POST, JSON body
    resp.raise_for_status()                              # raises on 4xx/5xx (E7 codes)
    data = resp.json()                                   # parse JSON response → dict

    # Same content-block structure as the SDK — a list of typed blocks (E3).
    return "".join(b["text"] for b in data["content"] if b["type"] == "text")


if __name__ == "__main__":
    print(ask_raw("In one sentence, what is REST?"))