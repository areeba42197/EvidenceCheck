"""Claim verification.

Semantic similarity measures textual/semantic relatedness and does not
independently establish factual correctness.
"""
from __future__ import annotations
from ..evaluation.metrics import reliability_summary

SUPPORTED, PARTIAL, UNSUPPORTED = "SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED"


class ClaimVerifier:
    def verify(self, claim: str, evidence: list[dict]) -> dict:
        raise NotImplementedError


class SimilarityVerifier(ClaimVerifier):
    def __init__(self, supported: float = 0.75, partial: float = 0.55):
        if partial > supported:
            raise ValueError("partial threshold must not exceed supported threshold")
        self.supported, self.partial = supported, partial

    def verify(self, claim: str, evidence: list[dict]) -> dict:
        if not evidence:
            return {"claim": claim, "verdict": UNSUPPORTED, "similarity": 0.0, "evidence": []}
        best = max(evidence, key=lambda e: e["similarity_score"])
        s = best["similarity_score"]
        v = SUPPORTED if s >= self.supported else PARTIAL if s >= self.partial else UNSUPPORTED
        return {"claim": claim, "verdict": v, "similarity": s, "evidence": evidence, "best_evidence": best}


def verify_answer(claims: list[dict], retriever, verifier: ClaimVerifier, top_k: int = 3) -> dict:
    results = []
    for c in claims:
        r = verifier.verify(c["claim"], retriever.retrieve(c["claim"], top_k))
        results.append({**c, **r})
    return {"claims": results, "summary": reliability_summary([r["verdict"] for r in results])}
