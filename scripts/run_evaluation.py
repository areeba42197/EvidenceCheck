"""Offline evaluation: retrieval metrics + verifier vs gold labels. No Groq needed."""
import json, _common  # noqa
from evidencecheck.config import Settings, DATA_RAW, RESULTS
from evidencecheck.ingestion.loaders import load_documents
from evidencecheck.ingestion.chunker import chunk_documents
from evidencecheck.retrieval.embeddings import SentenceTransformerEmbedder
from evidencecheck.retrieval.retriever import Retriever
from evidencecheck.verification.verifier import SimilarityVerifier
from evidencecheck.evaluation.evaluator import evaluate_verifier, evaluate_retrieval
s = Settings()
ret = Retriever(chunk_documents(load_documents(DATA_RAW), s.chunk_size, s.chunk_overlap), SentenceTransformerEmbedder(s.embedding_model))
out = {"retrieval": evaluate_retrieval(ret), "verification": evaluate_verifier(ret, SimilarityVerifier(s.supported_threshold, s.partial_threshold), s.top_k)}
(RESULTS / "tables").mkdir(parents=True, exist_ok=True)
(RESULTS / "tables" / "evaluation.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
print(json.dumps(out, indent=2))
