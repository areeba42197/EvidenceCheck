"""Configurable character chunking with overlap."""
from __future__ import annotations


def chunk_documents(docs: list[dict], chunk_size: int = 500, chunk_overlap: int = 100) -> list[dict]:
    if chunk_size <= 0 or not (0 <= chunk_overlap < chunk_size):
        raise ValueError("Require chunk_size > 0 and 0 <= chunk_overlap < chunk_size")
    step = chunk_size - chunk_overlap
    chunks: list[dict] = []
    counts: dict[str, int] = {}
    for d in docs:
        text = d["text"]
        for start in range(0, max(len(text), 1), step):
            piece = text[start:start + chunk_size].strip()
            if piece:
                n = counts.get(d["document_id"], 0)
                counts[d["document_id"]] = n + 1
                chunks.append({"chunk_id": f"{d['document_id']}_c{n:03d}", "document_id": d["document_id"],
                               "source": d["source"], "page": d.get("page"), "text": piece})
            if start + chunk_size >= len(text):
                break
    return chunks
