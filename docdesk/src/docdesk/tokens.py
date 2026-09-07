"""Token estimation for the Document Intelligence & Support Application.

Estimate tokens BEFORE sending (rough); verify with resp.usage AFTER (exact, S1 E4).
Rule of thumb (English): ~4 characters ≈ 1 token ≈ ¾ word.
"""

CHARS_PER_TOKEN = 4  # English rule-of-thumb approximation


def estimate_tokens(text: str) -> int:
    """Rough token estimate from character count. Approximate — not exact.

    For exact counts, use the response's usage fields after the call, or a
    tokenizer/count endpoint. This is for quick pre-send budgeting only.
    """
    return max(1, len(text) // CHARS_PER_TOKEN)


def estimate_request_tokens(system_prompt: str, user_content: str,
                            expected_output_tokens: int = 500) -> dict:
    """Estimate the full token ledger for a request: input (system + user) + output.

    Reminds us that EVERYTHING is tokens — system prompt, document, question, and reply.
    """
    input_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_content)
    return {
        "estimated_input_tokens": input_tokens,
        "estimated_output_tokens": expected_output_tokens,
        "estimated_total_tokens": input_tokens + expected_output_tokens,
    }


# Model context windows (tokens, input + output combined). Pinned in config ideally.
CONTEXT_WINDOWS = {
    "claude-sonnet-4-5": 200_000,
    "anthropic.claude-sonnet-4-5-20250101-v1:0": 200_000,
}


class ContextBudgetError(Exception):
    """Raised when a request's estimated tokens exceed the model's context window."""


def check_fits(model: str, system_prompt: str, user_content: str,
               expected_output_tokens: int) -> dict:
    """Estimate the token ledger and verify it fits the model's context window.

    Raises ContextBudgetError (a fix-it condition) if the estimate overflows —
    caught BEFORE sending, so we never retry an unfixable 400 overflow (E7).
    """
    window = CONTEXT_WINDOWS.get(model)
    est = estimate_request_tokens(system_prompt, user_content, expected_output_tokens)

    if window is not None and est["estimated_total_tokens"] > window:
        raise ContextBudgetError(
            f"Estimated {est['estimated_total_tokens']} tokens "
            f"(input {est['estimated_input_tokens']} + output {expected_output_tokens}) "
            f"exceeds the {window}-token window for {model}. "
            "Reduce input: prune history (session hygiene) or chunk/summarize the document."
        )
    return est


if __name__ == "__main__":
    from .config import SYSTEM_PROMPT
    big_doc = "clause text " * 60_000   # deliberately huge
    try:
        check_fits("claude-sonnet-4-5", SYSTEM_PROMPT, big_doc, expected_output_tokens=8000)
    except ContextBudgetError as e:
        print("Caught early:", e)

# if __name__ == "__main__":
#     from .config import SYSTEM_PROMPT
#     doc = "The refund window is 30 days from purchase. " * 50
#     print(estimate_request_tokens(SYSTEM_PROMPT, doc))