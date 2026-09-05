"""Concurrent realtime analysis for the Document Intelligence & Support Application.

Async path: many INDEPENDENT Claude calls whose waits overlap, for user-facing
"analyze all" where results are needed now. (Non-urgent bulk → use batch.py instead.)
"""
import asyncio
import logging
from anthropic import AsyncAnthropic
from .client import DEFAULT_MODEL, SYSTEM_PROMPT, extract_text

logger = logging.getLogger("docdesk.concurrent")
_aclient = AsyncAnthropic()


async def _summarize_one(doc, max_tokens: int = 1024) -> tuple[str, str]:
    """One async summarization; returns (doc_id, summary)."""
    resp = await _aclient.messages.create(
        model=DEFAULT_MODEL,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user",
                   "content": f"<document>\n{doc.text}\n</document>\n\nSummarize this document."}],
    )
    return (doc.id, extract_text(resp))


async def summarize_all(docs, max_tokens: int = 1024) -> dict[str, str]:
    """Summarize many documents concurrently (realtime; waits overlap).

    Use for user-facing 'analyze all' where results are needed now.
    For non-urgent bulk with nobody waiting, use batch.py (~50% cheaper).
    """
    results = await asyncio.gather(*(_summarize_one(d, max_tokens) for d in docs))
    logger.info("Summarized %d documents concurrently", len(results))
    return dict(results)


if __name__ == "__main__":
    class Doc:
        def __init__(self, id, text): self.id, self.text = id, text
    docs = [Doc("a", "Refund window is 30 days."), Doc("b", "Warranty lasts 1 year.")]
    print(asyncio.run(summarize_all(docs)))