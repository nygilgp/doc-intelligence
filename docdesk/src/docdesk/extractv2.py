"""extract.py (upgraded) — validated, defensively-parsed metadata extraction.

Connects to: client.py, orchestration.py. Upgrades the S1 extractor with the
full output-handling discipline: structured output + defensive parsing +
schema validation + content skepticism.
WHY: raw json.loads on model output crashes on code fences / preambles / missing
keys, and silently stores confidently-wrong or malformed values. Never trust
model output blindly \u2014 validate at the door.
"""
import json, re
from pydantic import BaseModel, ValidationError
from client import DocDeskClient

client = DocDeskClient()


class ContractMeta(BaseModel):
    party: str
    value_usd: float
    expiry: str                     # YYYY-MM-DD


_FENCE = re.compile(r"^```(?:json)?|```$", re.MULTILINE)


def _defensive_parse(text: str) -> dict | None:
    """Strip accidental code fences/preamble, then parse without crashing."""
    cleaned = _FENCE.sub("", text).strip()
    # Grab the first {...} block in case a preamble slipped through.
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def extract_meta(contract: str) -> ContractMeta | None:
    """Full pipeline: structured ask -> defensive parse -> validate -> sanity-check."""
    msg = client.create(
        system="Respond with ONLY a JSON object: party (string), value_usd "
               "(number, no currency symbols), expiry (YYYY-MM-DD). No prose.",
        max_tokens=256,
        messages=[{"role": "user", "content": f"<document>\n{contract}\n</document>"}],
    )
    parsed = _defensive_parse(msg.content[0].text)
    if parsed is None:
        return None                                   # malformed -> flag, don't crash

    try:
        meta = ContractMeta(**parsed)                 # schema + type validation
    except ValidationError:
        return None                                   # wrong shape -> reject

    if not (0 < meta.value_usd < 1_000_000_000):      # skepticism: sanity-check value
        return None                                   # implausible -> flag for review
    return meta