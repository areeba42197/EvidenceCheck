import json, _common  # noqa
import numpy as np
from evidencecheck.config import Settings, ROOT
from evidencecheck.retrieval.embeddings import SentenceTransformerEmbedder
p = ROOT / "data" / "processed"
chunks = json.loads((p / "chunks.json").read_text(encoding="utf-8"))
vecs = SentenceTransformerEmbedder(Settings().embedding_model).encode([c["text"] for c in chunks])
np.save(p / "embeddings.npy", vecs)
print(f"saved {vecs.shape} embeddings (the app also rebuilds the index in memory at startup)")
