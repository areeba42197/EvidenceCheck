import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from evidencecheck.ingestion.chunker import chunk_documents
from evidencecheck.retrieval.embeddings import HashEmbedder
from evidencecheck.retrieval.retriever import Retriever
from evidencecheck.claims.extractor import extract_claims, extract_claims_basic
from evidencecheck.verification.verifier import SimilarityVerifier, verify_answer
from evidencecheck.evaluation.metrics import reliability_summary, classification_report, recall_precision_at_k
from evidencecheck.generation.providers import GroqProvider, ProviderError

DOCS = [{"document_id": "d1", "source": "d1.txt", "page": None,
         "text": "The Eiffel Tower was completed in 1889. It is located in Paris. " * 20}]


def test_chunking_overlap_and_ids():
    ch = chunk_documents(DOCS, 200, 50)
    assert len(ch) > 1 and len({c["chunk_id"] for c in ch}) == len(ch)
    assert all(len(c["text"]) <= 200 for c in ch)


def test_chunking_invalid_and_empty():
    with pytest.raises(ValueError):
        chunk_documents(DOCS, 100, 100)
    assert chunk_documents([], 100, 10) == []


def test_retrieval_empty_and_topk():
    assert Retriever([], HashEmbedder()).retrieve("x") == []
    r = Retriever(chunk_documents(DOCS, 200, 50), HashEmbedder())
    res = r.retrieve("Eiffel Tower completed", 3)
    assert len(res) == 3 and res[0]["similarity_score"] >= res[1]["similarity_score"]


def test_claim_extraction_dedup_and_empty():
    cl = extract_claims_basic("The tower opened in 1889. The tower opened in 1889. It is in Paris.")
    assert len(cl) == 2 and cl[0]["category"] == "date"
    assert extract_claims("") == []


def test_verifier_thresholds_and_no_evidence():
    v = SimilarityVerifier(0.75, 0.55)
    ev = lambda s: [{"similarity_score": s}]
    assert v.verify("c", ev(0.8))["verdict"] == "SUPPORTED"
    assert v.verify("c", ev(0.6))["verdict"] == "PARTIALLY_SUPPORTED"
    assert v.verify("c", ev(0.1))["verdict"] == "UNSUPPORTED"
    assert v.verify("c", [])["verdict"] == "UNSUPPORTED"
    with pytest.raises(ValueError):
        SimilarityVerifier(0.5, 0.9)


def test_verify_answer_pipeline():
    r = Retriever(chunk_documents(DOCS, 200, 50), HashEmbedder())
    out = verify_answer(extract_claims_basic("The Eiffel Tower was completed in 1889."), r, SimilarityVerifier(), 3)
    assert out["summary"]["total"] == 1


def test_metrics():
    s = reliability_summary(["SUPPORTED"] * 7 + ["PARTIALLY_SUPPORTED"] * 2 + ["UNSUPPORTED"])
    assert s["reliability"] == 0.7 and s["partial_rate"] == 0.2 and s["unsupported_rate"] == 0.1
    assert reliability_summary([])["reliability"] is None
    assert classification_report([], []) is None
    rep = classification_report(["SUPPORTED", "UNSUPPORTED"], ["SUPPORTED", "SUPPORTED"])
    assert rep["per_label"]["SUPPORTED"]["recall"] == 1.0
    assert recall_precision_at_k(["a"], set(), 1) is None
    assert recall_precision_at_k(["a", "b"], {"a"}, 2)["precision"] == 0.5


def test_no_api_key_is_graceful():
    with pytest.raises(ProviderError, match="not configured"):
        GroqProvider("m", api_key="").generate("hi")


def test_error_analysis_roundtrip(tmp_path):
    from evidencecheck.evaluation.error_analysis import add_case, load_cases, category_counts
    p = tmp_path / "e.csv"
    add_case({"case_id": "1", "question": "q", "category": "date_error"}, p)
    assert category_counts(load_cases(p)) == {"date_error": 1}
    with pytest.raises(ValueError):
        add_case({"category": "bogus"}, p)


def test_evaluators_na_without_gold(tmp_path, monkeypatch):
    from evidencecheck.evaluation import evaluator
    from evidencecheck.evaluation.evaluator import evaluate_verifier, evaluate_retrieval
    monkeypatch.setattr(evaluator, 'EVAL_DIR', tmp_path)
    r = Retriever(chunk_documents(DOCS, 200, 50), HashEmbedder())
    assert evaluate_verifier(r, SimilarityVerifier())["status"].startswith("N/A")
    assert evaluate_retrieval(r)["status"].startswith("N/A")


def test_groq_model_fallback(monkeypatch):
    import requests
    calls = []
    class R:
        def __init__(s, c, j): s.status_code, s._j = c, j
        def json(s): return s._j
    def fake(url, json, **kw):
        calls.append(json["model"])
        return R(404, {"error": {"message": "gone"}}) if json["model"] == "old" else R(200, {"choices": [{"message": {"content": "ok"}}]})
    monkeypatch.setattr(requests, "post", fake)
    p = GroqProvider("old", api_key="k")
    assert p.generate("hi") == "ok" and calls == ["old", "openai/gpt-oss-120b"] and p.active_model == "openai/gpt-oss-120b"


def test_gemini_provider_fallback_and_parsing(monkeypatch):
    import requests
    from evidencecheck.generation.providers import GeminiProvider, make_provider
    from evidencecheck.config import Settings
    urls = []
    class R:
        def __init__(s, c, j): s.status_code, s._j = c, j
        def json(s): return s._j
    def fake(url, json, headers, **kw):
        urls.append(url)
        assert headers["x-goog-api-key"] == "k"
        if "old-model" in url:
            return R(404, {"error": {"message": "not found"}})
        return R(200, {"candidates": [{"content": {"parts": [{"text": "he"}, {"text": "llo"}]}}]})
    monkeypatch.setattr(requests, "post", fake)
    p = GeminiProvider("old-model", api_key="k")
    assert p.generate("hi") == "hello" and p.active_model == "gemini-3.1-flash-lite"
    with pytest.raises(ProviderError, match="not configured"):
        GeminiProvider("m", api_key="").generate("x")
    assert isinstance(make_provider(Settings(llm_provider="groq"), "k"), GroqProvider)


def test_runner_and_evaluator_with_fake_provider():
    from evidencecheck.experiments.runner import run, load_questions
    from evidencecheck.evaluation.evaluator import evaluate_verifier, threshold_sweep, evaluate_retrieval
    from evidencecheck.ingestion.loaders import load_documents
    from evidencecheck.config import DATA_RAW
    class Fake:
        configured, model = True, "fake"
        def generate(self, prompt): return "Python was first released in 1991. Photosynthesis happens in chloroplasts."
    docs = load_documents(DATA_RAW)
    out = run("top-k", HashEmbedder(), Fake(), load_questions()[:2], docs)
    assert len(out["results"]) == 3 and out["results"][0]["total"] > 0
    with pytest.raises(RuntimeError):
        class NoKey: configured = False
        run("top-k", HashEmbedder(), NoKey(), None, docs)
    r = Retriever(chunk_documents(docs, 500, 100), HashEmbedder())
    ev = evaluate_verifier(r, SimilarityVerifier(), 3)
    assert ev["n_gold_claims"] == 17 and len(ev["rows"]) == 17
    assert len(threshold_sweep(r)) == 10 and evaluate_retrieval(r)["status"] == "ok"
