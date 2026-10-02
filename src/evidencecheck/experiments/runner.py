"""Experiments on the bundled demo questions (or your own). Works with any LLMProvider."""
from __future__ import annotations
import json
from ..config import Settings, EVAL_DIR, RESULTS, DATA_RAW
from ..ingestion.loaders import load_documents
from ..ingestion.chunker import chunk_documents
from ..retrieval.retriever import Retriever
from ..generation.rag import direct_answer, rag_answer
from ..claims.extractor import extract_claims
from ..verification.verifier import SimilarityVerifier, verify_answer
from ..evaluation.metrics import reliability_summary


def load_questions() -> list[dict]:
    p = EVAL_DIR / "questions.json"
    qs = json.loads(p.read_text(encoding="utf-8")) if p.exists() else []
    if not qs:
        raise FileNotFoundError("data/evaluation/questions.json is empty. Add questions first.")
    return qs


def n_steps(name: str, n_questions: int) -> int:
    return n_questions * {"top-k": 3, "chunk-size": 3, "baseline": 2}[name]


def run_config(embedder, provider, s: Settings, questions, docs, tick=None) -> dict:
    ret = Retriever(chunk_documents(docs, s.chunk_size, s.chunk_overlap), embedder)
    ver = SimilarityVerifier(s.supported_threshold, s.partial_threshold)
    verdicts = []
    for q in questions:
        ans, _ = rag_answer(q["question"], ret, provider, s.top_k)
        verdicts += [c["verdict"] for c in verify_answer(extract_claims(ans, provider), ret, ver, s.top_k)["claims"]]
        if tick:
            tick()
    return {"config": {"top_k": s.top_k, "chunk_size": s.chunk_size}, "n_questions": len(questions),
            **reliability_summary(verdicts)}


def run(name: str, embedder, provider, questions=None, docs=None, base: Settings | None = None, tick=None) -> dict:
    if not getattr(provider, "configured", False):
        raise RuntimeError("LLM API key not configured. Experiments need generation.")
    base, qs = base or Settings(), questions or load_questions()
    docs = docs if docs is not None else load_documents(DATA_RAW)
    if name == "top-k":
        res = [run_config(embedder, provider, Settings(top_k=k), qs, docs, tick) for k in (1, 3, 5)]
    elif name == "chunk-size":
        res = [run_config(embedder, provider, Settings(chunk_size=c, chunk_overlap=min(100, c // 4)), qs, docs, tick)
               for c in (200, 500, 800)]
    elif name == "baseline":
        # Direct-LLM claims are checked against the same corpus: measures corpus support, not truth.
        ret = Retriever(chunk_documents(docs, base.chunk_size, base.chunk_overlap), embedder)
        ver, direct = SimilarityVerifier(base.supported_threshold, base.partial_threshold), []
        for q in qs:
            direct += [c["verdict"] for c in verify_answer(extract_claims(direct_answer(q["question"], provider)), ret, ver)["claims"]]
            if tick:
                tick()
        res = [{"system": "direct_llm", "n_questions": len(qs), **reliability_summary(direct)},
               {"system": "rag_verified", **run_config(embedder, provider, base, qs, docs, tick)}]
    else:
        raise ValueError(f"Unknown experiment: {name}")
    out = {"experiment": name, "model": getattr(provider, "model", "unknown"), "results": res}
    try:  # disk is ephemeral on Streamlit Cloud; the app keeps results in session + offers download
        (RESULTS / "tables").mkdir(parents=True, exist_ok=True)
        (RESULTS / "tables" / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    except OSError:
        pass
    return out
