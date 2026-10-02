"""Offline evaluation against gold labels (no LLM needed)."""
from __future__ import annotations
import json
from ..config import EVAL_DIR
from ..verification.verifier import SimilarityVerifier
from .metrics import classification_report, recall_precision_at_k


def _load(name: str) -> list[dict]:
    p = EVAL_DIR / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def evaluate_verifier(retriever, verifier: SimilarityVerifier, top_k: int = 3) -> dict:
    """Verifier vs gold claim labels; includes per-claim rows. 'N/A' without gold labels."""
    gold = _load("gold_claims.json")
    if not gold:
        return {"status": "N/A — no gold labels available.", "rows": []}
    rows = []
    for g in gold:
        r = verifier.verify(g["claim"], retriever.retrieve(g["claim"], top_k))
        rows.append({"claim_id": g["claim_id"], "question_id": g.get("question_id", ""), "claim": g["claim"],
                     "gold": g["label"], "pred": r["verdict"], "similarity": r["similarity"],
                     "evidence": (r.get("best_evidence") or {}).get("text", "")})
    rep = classification_report([r["gold"] for r in rows], [r["pred"] for r in rows])
    return {"status": "ok", "n_gold_claims": len(gold), "rows": rows, **rep}


def threshold_sweep(retriever, top_k: int = 3, partial: float = 0.55) -> list[dict]:
    """Macro-F1 / accuracy vs the supported threshold, on gold claims. [] without gold."""
    gold = _load("gold_claims.json")
    if not gold:
        return []
    ev = [retriever.retrieve(g["claim"], top_k) for g in gold]
    out = []
    for i in range(10):
        t = round(0.5 + 0.05 * i, 2)
        v = SimilarityVerifier(t, min(partial, t))
        pred = [v.verify(g["claim"], e)["verdict"] for g, e in zip(gold, ev)]
        lab = [g["label"] for g in gold]
        out.append({"supported_threshold": t, "macro_f1": classification_report(lab, pred)["macro_f1"],
                    "accuracy": sum(a == b for a, b in zip(lab, pred)) / len(lab)})
    return out


def evaluate_retrieval(retriever, ks=(1, 3, 5)) -> dict:
    """Document-level Recall@K / Precision@K from questions[].source_document."""
    qs = [q for q in _load("questions.json") if q.get("source_document")]
    if not qs:
        return {"status": "N/A — no questions with source_document."}
    out = {"status": "ok", "n_questions": len(qs)}
    for k in ks:
        rows = [recall_precision_at_k([c["document_id"] for c in retriever.retrieve(q["question"], k)],
                                      {q["source_document"]}, k) for q in qs]
        out[f"recall@{k}"] = sum(r["recall"] for r in rows) / len(rows)
        out[f"precision@{k}"] = sum(r["precision"] for r in rows) / len(rows)
    return out
