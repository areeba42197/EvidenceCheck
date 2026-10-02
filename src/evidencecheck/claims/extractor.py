"""Claim extraction: sentence-level baseline, optional Groq structured extraction."""
from __future__ import annotations
import json, re

_SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")


def categorize(claim: str) -> str:
    if re.search(r"\b(1[0-9]{3}|20[0-9]{2})\b", claim):
        return "date"
    if re.search(r"\d", claim):
        return "numerical"
    if re.search(r"\b(because|due to|causes?|led to|results? in)\b", claim, re.I):
        return "causal"
    if re.search(r"\b(more|less|larger|smaller|than|higher|lower)\b", claim, re.I):
        return "comparative"
    return "factual"


def extract_claims_basic(answer: str) -> list[dict]:
    seen, out = set(), []
    for s in _SENT.split(answer.strip()):
        for part in s.split(";"):
            c = part.strip()
            key = re.sub(r"\W+", " ", c.lower()).strip()
            if len(key.split()) < 3 or key in seen:
                continue
            seen.add(key)
            out.append({"claim_id": f"c{len(out)+1:03d}", "claim": c, "category": categorize(c)})
    return out


def extract_claims(answer: str, provider=None) -> list[dict]:
    """Hybrid: try LLM atomic extraction, fall back to sentence-level."""
    if provider is not None and getattr(provider, "configured", False):
        try:
            raw = provider.generate("Split the text into atomic factual claims. Return ONLY a JSON "
                                    f"list of strings.\n\nText:\n{answer}")
            items = json.loads(re.sub(r"```(json)?", "", raw).strip())
            claims = [str(x).strip() for x in items if str(x).strip()]
            if claims:
                return [{"claim_id": f"c{i+1:03d}", "claim": c, "category": categorize(c)}
                        for i, c in enumerate(dict.fromkeys(claims))]
        except Exception:
            pass
    return extract_claims_basic(answer)
