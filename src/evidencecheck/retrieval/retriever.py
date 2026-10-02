from __future__ import annotations
from .index import VectorIndex


class Retriever:
    def __init__(self, chunks: list[dict], embedder):
        self.chunks, self.embedder = chunks, embedder
        self.index = VectorIndex(embedder.encode([c["text"] for c in chunks])) if chunks else None

    def retrieve(self, query: str, top_k: int = 3, min_similarity: float | None = None) -> list[dict]:
        if self.index is None or not query.strip():
            return []
        scores, idx = self.index.search(self.embedder.encode([query]), top_k)
        out = []
        for s, i in zip(scores[0], idx[0]):
            if min_similarity is not None and s < min_similarity:
                continue
            out.append({**self.chunks[int(i)], "similarity_score": float(s)})
        return out
