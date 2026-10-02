"""Vector index: FAISS (inner product on normalised vectors) with NumPy fallback."""
from __future__ import annotations
import numpy as np

try:
    import faiss  # type: ignore
except ImportError:  # pragma: no cover
    faiss = None


class VectorIndex:
    def __init__(self, vectors: np.ndarray):
        self.vectors = np.ascontiguousarray(vectors, dtype="float32")
        self._faiss = None
        if faiss is not None and len(self.vectors):
            self._faiss = faiss.IndexFlatIP(self.vectors.shape[1])
            self._faiss.add(self.vectors)

    def search(self, q: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
        k = min(k, len(self.vectors))
        if k == 0:
            return np.zeros((len(q), 0), "float32"), np.zeros((len(q), 0), int)
        if self._faiss is not None:
            return self._faiss.search(np.ascontiguousarray(q, dtype="float32"), k)
        sims = q @ self.vectors.T
        idx = np.argsort(-sims, axis=1)[:, :k]
        return np.take_along_axis(sims, idx, axis=1), idx
