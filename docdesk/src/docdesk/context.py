"""context.py — context engineering for docdesk's document chat.

Connects to: session.py (multi-turn state), client.py (the summarizing call).
WHY: re-sending the full document + full history every turn causes BLOAT (cost,
latency) and DRIFT (quality loss). We PRUNE the document to the relevant slice
and COMPACT distant history into a running summary, keeping recent turns verbatim.
"""
from client import DocDeskClient

client = DocDeskClient()
KEEP_RECENT = 4          # keep the last N turns verbatim (most relevant)


def prune_document(doc_sections: dict[str, str], question: str) -> str:
    """PRUNE: select only the section(s) relevant to this question, not all 80 pages.
    (A real impl would use retrieval/embeddings; keyword match shown for clarity.)"""
    q = question.lower()
    relevant = {name: text for name, text in doc_sections.items()
                if any(w in text.lower() for w in q.split() if len(w) > 4)}
    chosen = relevant or doc_sections          # fall back to all if nothing matched
    return "\n\n".join(f"[{n}]\n{t}" for n, t in chosen.items())


def compact_history(turns: list[dict]) -> list[dict]:
    """COMPACT: summarize the DISTANT turns into one running-summary note,
    keep the most recent KEEP_RECENT turns verbatim. Preserves load-bearing
    facts while shedding verbatim bulk. This is selective, not blind truncation."""
    if len(turns) <= KEEP_RECENT:
        return turns                            # nothing to compact yet

    old, recent = turns[:-KEEP_RECENT], turns[-KEEP_RECENT:]
    convo = "\n".join(f"{t['role']}: {t['content']}" for t in old)
    summary = client.create(
        max_tokens=256,
        system="Summarize this conversation so far in 2-3 sentences. PRESERVE any "
               "specific facts the user established (names, dates, which document).",
        messages=[{"role": "user", "content": convo}],
    )
    note = {"role": "user",
            "content": f"[Summary of earlier conversation]\n{summary.content[0].text}"}
    return [note] + recent


def build_chat_context(doc_sections, turns, question) -> list[dict]:
    """Assemble a LEAN window: compacted history + a fresh user turn carrying
    only the pruned, relevant document slice."""
    messages = compact_history(turns)
    messages.append({
        "role": "user",
        "content": f"Relevant document sections:\n"
                   f"<document>\n{prune_document(doc_sections, question)}\n</document>\n\n"
                   f"Question: {question}",
    })
    return messages