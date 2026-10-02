import json, _common  # noqa
from evidencecheck.config import Settings, DATA_RAW, ROOT
from evidencecheck.ingestion.loaders import load_documents
from evidencecheck.ingestion.chunker import chunk_documents
s = Settings()
chunks = chunk_documents(load_documents(DATA_RAW), s.chunk_size, s.chunk_overlap)
out = ROOT / "data" / "processed" / "chunks.json"
out.write_text(json.dumps(chunks, indent=1), encoding="utf-8")
print(f"{len(chunks)} chunks -> {out}")
