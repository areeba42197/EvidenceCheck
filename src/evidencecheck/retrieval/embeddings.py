"""Embedders. HashEmbedder is a lexical stand-in for tests/offline use only."""
from __future__ import annotations
import re, zlib
import numpy as np


class SentenceTransformerEmbedder:
    def __init__(self, name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.name = name
        self.model = SentenceTransformer(name)

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, normalize_embeddings=True), dtype="float32")


class HashEmbedder:
    """Bag-of-words hashing embedder. NOT semantic; for tests only."""
    name = "hash-test-embedder"

    def __init__(self, dim: int = 256):
        self.dim = dim

    def encode(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype="float32")
        for i, t in enumerate(texts):
            for w in re.findall(r"\w+", t.lower()):
                out[i, zlib.crc32(w.encode()) % self.dim] += 1
        n = np.linalg.norm(out, axis=1, keepdims=True)
        return out / np.maximum(n, 1e-9)
