# docdesk/response_utils.py
#
# NEW MODULE (see S2 E6 — Thinking Modes)
#
# On current-generation models, thinking is on by default, so a response's
# content array can begin with one or more `thinking` blocks before the first
# `text` block. Code that assumes content[0] is always the answer will break.
# This module selects blocks by their `type` field instead of by position --
# the correct, forward-compatible pattern regardless of whether thinking is
# on, off, or adaptive for a given request.

from anthropic.types import Message


def get_text_block(response: Message) -> str:
    """Return the first text block's content from a Messages API response.

    Selects by type, NOT position -- safe whether or not the response
    contains thinking blocks before the text block.
    """
    text_block = next(
        (block for block in response.content if block.type == "text"), None
    )
    if text_block is None:
        raise ValueError(
            "No text block found in response.content -- "
            f"got block types: {[b.type for b in response.content]}"
        )
    return text_block.text


def get_thinking_block(response: Message):
    """Return the first thinking block, if present, else None.

    Useful for logging/inspecting reasoning, or for passing thinking blocks
    back UNMODIFIED in a multi-turn tool-use loop (required -- do not trim
    or edit thinking blocks before sending them back).
    """
    return next(
        (block for block in response.content if block.type == "thinking"), None
    )