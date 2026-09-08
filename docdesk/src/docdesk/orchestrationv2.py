"""orchestration.py (extended) — focused-subagent retrieval over document sections.

Connects to: client.py (Claude calls). Builds on the manager pattern from S3 E2.
KEY PATTERN: each subagent sees ONLY one section + the question, in its own
context window, and returns a CONCISE extract. This is a QUALITY lever, not just
a capacity one — focus sharpens each extract even when the whole manual would fit.
"""
from client import DocDeskClient

client = DocDeskClient()


def _section_extractor(section_name: str, section_text: str, question: str) -> dict:
    """A focused subagent: clean context, one section, one job."""
    msg = client.create(
        max_tokens=400,
        system=(
            f"You extract facts from the '{section_name}' section ONLY. "
            "Return just the facts relevant to the user's question, concisely. "
            "If nothing in this section is relevant, say 'No relevant facts.'"
        ),
        messages=[{
            "role": "user",
            "content": f"QUESTION: {question}\n\nSECTION ({section_name}):\n{section_text}",
        }],
    )
    return {"section": section_name, "extract": msg.content[0].text}


def answer_from_sections(question: str, sections: dict[str, str]) -> str:
    """Manager: dispatch a focused extractor per relevant section, then synthesize.
    Each extractor reasons over a CLEAN, single-section context."""
    extracts = [
        _section_extractor(name, text, question)
        for name, text in sections.items()
    ]

    # Synthesis context holds only the concise extracts — never the full sections.
    joined = "\n\n".join(f"[{e['section']}]\n{e['extract']}" for e in extracts)
    final = client.create(
        max_tokens=800,
        system="Synthesize these section extracts into one accurate answer. "
               "Cite which section each fact came from.",
        messages=[{"role": "user", "content": f"QUESTION: {question}\n\n{joined}"}],
    )
    return final.content[0].text


if __name__ == "__main__":
    manual = {
        "installation":   "…install steps…",
        "troubleshooting":"…error codes…",
        "warranty":       "…coverage terms…",
    }
    print(answer_from_sections("Does a failed install void the warranty?", manual))