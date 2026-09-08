"""orchestration.py (extended) — manager/subagent coordination for contract risk.

Connects to: client.py (Claude calls). Builds on the workflow scaffold from S3 E1.
KEY PATTERN: each subagent call receives ONLY its own rulebook + the contract,
in its OWN message list (its own context window). The privacy worker never sees
the financial rulebook. The manager holds only compact reports, not transcripts.

NOTE: This is still a coordinator WE own. The autonomous agent loop arrives in
S3 E4 — this episode is about the context-isolation boundary, which matters
regardless of whether a loop drives it.
"""
from client import DocDeskClient

client = DocDeskClient()

RULEBOOKS = {
    "financial": "…financial-terms rules…",
    "liability": "…liability-clause rules…",
    "privacy":   "…data-privacy compliance rules…",
}


def _worker(specialty: str, rulebook: str, contract: str) -> dict:
    """A subagent: isolated context — sees ONLY its rulebook + the contract.
    Returns a COMPACT report, not its full reasoning."""
    msg = client.create(
        max_tokens=512,
        system=(
            f"You are a {specialty} risk reviewer. Assess ONLY {specialty} risk. "
            "Return 2-3 bullet findings. Be terse."
        ),
        messages=[{
            "role": "user",
            "content": f"RULEBOOK:\n{rulebook}\n\nCONTRACT:\n{contract}",
        }],
    )
    return {"specialty": specialty, "findings": msg.content[0].text}


def review_contract(contract: str) -> str:
    """Manager: delegates 3 isolated subtasks, then synthesizes.
    Each worker runs in its OWN context; the manager sees only their reports."""
    reports = [
        _worker(spec, book, contract)
        for spec, book in RULEBOOKS.items()
    ]

    # Manager synthesis: only the compact reports enter this context, not the
    # rulebooks or the workers' intermediate reasoning.
    joined = "\n\n".join(f"[{r['specialty']}]\n{r['findings']}" for r in reports)
    summary = client.create(
        max_tokens=1024,
        system="You are the lead reviewer. Merge these findings into ONE risk report.",
        messages=[{"role": "user", "content": joined}],
    )
    return summary.content[0].text


if __name__ == "__main__":
    print(review_contract("…contract text…"))