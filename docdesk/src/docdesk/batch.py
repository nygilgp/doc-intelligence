"""Batch processing for the Document Intelligence & Support Application.

Implements ADR 0001's batch lane: latency-tolerant, high-volume document work
at ~50% lower cost, via submit → poll → retrieve.
"""
import time
import logging
from anthropic import Anthropic
from .client import DEFAULT_MODEL, SYSTEM_PROMPT, extract_text

logger = logging.getLogger("docdesk.batch")
_client = Anthropic()


def submit_summaries(docs) -> str:
    """Submit a batch of summarization requests. Returns the batch ID.

    `docs` is an iterable of objects with `.id` and `.text`.
    Each request carries a custom_id so we can match results back to documents.
    """
    batch = _client.messages.batches.create(
        requests=[
            {
                "custom_id": f"doc-{doc.id}",
                "params": {
                    "model": DEFAULT_MODEL,
                    "max_tokens": 1024,
                    "system": SYSTEM_PROMPT,
                    "messages": [{
                        "role": "user",
                        "content": f"<document>\n{doc.text}\n</document>\n\nSummarize this document.",
                    }],
                },
            }
            for doc in docs
        ]
    )
    logger.info("Submitted batch %s", batch.id)
    return batch.id


def wait_for_batch(batch_id: str, poll_seconds: int = 60):
    """Poll until the batch has ended. (For very long batches, prefer a scheduled
    job over a blocking loop — but this shows the lifecycle clearly.)"""
    while True:
        batch = _client.messages.batches.retrieve(batch_id)
        if batch.processing_status == "ended":
            logger.info("Batch %s ended", batch_id)
            return
        logger.info("Batch %s status=%s; waiting", batch_id, batch.processing_status)
        time.sleep(poll_seconds)


def collect_summaries(batch_id: str) -> dict[str, str]:
    """Retrieve results, matching each to its document via custom_id.

    Returns {custom_id: summary}. Per-result errors are logged, not fatal —
    a batch is not all-or-nothing.
    """
    summaries: dict[str, str] = {}
    for result in _client.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            summaries[result.custom_id] = extract_text(result.result.message)
        else:
            logger.warning("Result %s failed: %s", result.custom_id, result.result.type)
    return summaries