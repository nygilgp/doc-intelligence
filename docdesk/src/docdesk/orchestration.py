"""orchestration.py — deterministic document-processing workflow.

Connects to: client.py (Claude calls), extract.py (structured output).
This is a WORKFLOW: the path is fixed and owned by this code, not by Claude.
When a task's path genuinely can't be known ahead of time, escalate to the
agent loop (added in S3 E4) — not before.
"""
from client import DocDeskClient
from extract import extract_structured

client = DocDeskClient()  # your vendor-flexible Anthropic/Bedrock client


def summarize(text: str) -> str:
    msg = client.create(
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": f"Summarize this document in 3-4 sentences:\n\n{text}",
        }],
    )
    return msg.content[0].text


def classify(summary: str) -> str:
    # Reuses your structured-extraction helper for a constrained category.
    result = extract_structured(
        text=summary,
        schema={"category": "one of: invoice, contract, report, other"},
    )
    return result["category"]


def process_document(doc_id: str, text: str) -> dict:
    """Fixed 3-step path: summarize -> classify -> assemble record.
    You can draw this flowchart before running it => it's a workflow.
    """
    summary = summarize(text)
    category = classify(summary)
    record = {"doc_id": doc_id, "summary": summary, "category": category}
    return record


if __name__ == "__main__":
    demo = process_document("doc-001", "Acme Corp Q3 invoice, amount due $4,200...")
    print(demo)