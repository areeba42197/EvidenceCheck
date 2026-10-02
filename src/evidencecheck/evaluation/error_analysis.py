"""Error-analysis CSV helpers. Cases must be reviewed by a human; none are auto-fabricated."""
from __future__ import annotations
import csv
from pathlib import Path
from ..config import RESULTS

CATEGORIES = ["wrong_retrieval", "insufficient_context", "partial_support", "contradictory_evidence",
              "numerical_error", "entity_error", "date_error", "multi_hop_failure",
              "claim_extraction_error", "verification_error", "generation_error"]
FIELDS = ["case_id", "question", "claim", "evidence", "verdict", "category", "analysis"]
PATH = RESULTS / "error_analysis.csv"


def load_cases(path: Path = PATH) -> list[dict]:
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def add_case(row: dict, path: Path = PATH) -> None:
    if row.get("category") not in CATEGORIES:
        raise ValueError(f"category must be one of {CATEGORIES}")
    new = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in FIELDS})


def category_counts(cases: list[dict]) -> dict[str, int]:
    return {c: sum(r["category"] == c for r in cases) for c in CATEGORIES if any(r["category"] == c for r in cases)}
