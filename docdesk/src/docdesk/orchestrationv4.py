"""orchestration.py (extended) — isolated multi-step contract analysis.

Connects to: client.py, prompts.py, context.py (pruning). Builds on the workflow
pattern (S3 E1) and subagent isolation (S3 E2/E3).
WHY isolate: summary, dates, and risk are SEPARABLE concerns needing DIFFERENT
context (only the risk step needs the big rubric). Running them in one context
would bloat (rubric present during summary) and drift (concerns interleave).
Each step below gets a FRESH, focused context holding only what it needs.
"""
from client import DocDeskClient
from prompts import build_summarize_prompt

client = DocDeskClient()


def _summary_step(contract: str) -> str:
    # Isolated context: contract only. No rubric, no other concerns.
    msg = client.create(max_tokens=256,
                        messages=[{"role": "user", "content": build_summarize_prompt(contract)}])
    return msg.content[0].text.strip()


def _dates_step(contract: str) -> str:
    # Isolated context: contract only. Fresh window, single concern.
    msg = client.create(
        max_tokens=256,
        system="Extract key dates as a bullet list: label + date. Nothing else.",
        messages=[{"role": "user", "content": f"<document>\n{contract}\n</document>"}],
    )
    return msg.content[0].text.strip()


def _risk_step(contract: str, risk_rubric: str) -> str:
    # Isolated context: the big rubric enters ONLY here, where it's needed.
    # If this grows heavy, promote it to a subagent returning a compact finding.
    msg = client.create(
        max_tokens=512,
        system="You are a risk reviewer. Assess the contract against the rubric. "
               "Return 3-5 bullet findings.",
        messages=[{"role": "user",
                   "content": f"RUBRIC:\n{risk_rubric}\n\n<document>\n{contract}\n</document>"}],
    )
    return msg.content[0].text.strip()


def analyze_contract(contract: str, risk_rubric: str) -> dict:
    """Three ISOLATED steps, each a fresh focused context. Nothing to prune,
    nothing drifts \u2014 crowding is prevented, not cleaned up."""
    return {
        "summary": _summary_step(contract),        # context: contract
        "key_dates": _dates_step(contract),         # context: contract
        "risk": _risk_step(contract, risk_rubric),  # context: contract + rubric
    }


if __name__ == "__main__":
    from pprint import pprint
    pprint(analyze_contract("…contract text…", "…large risk rubric…"))