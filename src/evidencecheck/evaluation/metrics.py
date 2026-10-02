"""Metrics. Return None when ground truth is missing; never invent numbers."""
from __future__ import annotations
from collections import Counter

LABELS = ["SUPPORTED", "PARTIALLY_SUPPORTED", "UNSUPPORTED"]


def reliability_summary(verdicts: list[str]) -> dict:
    n = len(verdicts)
    if n == 0:
        return {"total": 0, "reliability": None, "support_rate": None, "partial_rate": None,
                "unsupported_rate": None, "counts": {l: 0 for l in LABELS}}
    c = Counter(verdicts)
    return {"total": n, "reliability": c[LABELS[0]] / n, "support_rate": c[LABELS[0]] / n,
            "partial_rate": c[LABELS[1]] / n, "unsupported_rate": c[LABELS[2]] / n,
            "counts": {l: c[l] for l in LABELS}}


def recall_precision_at_k(retrieved_docs: list[str], relevant_docs: set[str], k: int) -> dict | None:
    """Document-level retrieval metrics; None without gold relevance."""
    if not relevant_docs:
        return None
    top = retrieved_docs[:k]
    hits = len({d for d in top if d in relevant_docs})
    return {"recall": hits / len(relevant_docs), "precision": sum(d in relevant_docs for d in top) / max(len(top), 1)}


def classification_report(gold: list[str], pred: list[str]) -> dict | None:
    """Per-label precision/recall/F1 and confusion matrix; None without gold labels."""
    if not gold or len(gold) != len(pred):
        return None
    per = {}
    for l in LABELS:
        tp = sum(g == l and p == l for g, p in zip(gold, pred))
        fp = sum(g != l and p == l for g, p in zip(gold, pred))
        fn = sum(g == l and p != l for g, p in zip(gold, pred))
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        per[l] = {"precision": pr, "recall": rc, "f1": 2 * pr * rc / (pr + rc) if pr + rc else 0.0}
    cm = {g: {p: sum(a == g and b == p for a, b in zip(gold, pred)) for p in LABELS} for g in LABELS}
    return {"per_label": per, "confusion_matrix": cm, "macro_f1": sum(v["f1"] for v in per.values()) / len(LABELS)}
