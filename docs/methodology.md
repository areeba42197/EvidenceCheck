# Methodology
Pipeline: ingest -> chunk (default 500/100) -> MiniLM embeddings -> FAISS top-k -> Groq answer -> claim extraction -> per-claim retrieval -> similarity verdict (>=0.75 supported, >=0.55 partial) -> reliability = supported / verifiable claims.
Semantic similarity measures relatedness, not factual correctness. EvidenceCheck estimates whether claims are supported by retrieved evidence; it does not determine truth.
Experiments: baseline (direct vs RAG+verify), top-k {1,3,5}, chunk size {200,500,800}. Baseline caveat: direct-LLM claims are checked against the same corpus, so the number reflects corpus support, not truth.
