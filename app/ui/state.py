"""Shared cached resources and session state."""
import os
import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from evidencecheck.config import Settings, DATA_RAW, RESULTS  # noqa: E402
from evidencecheck.ingestion.loaders import load_documents  # noqa: E402
from evidencecheck.ingestion.chunker import chunk_documents  # noqa: E402
from evidencecheck.retrieval.retriever import Retriever  # noqa: E402
from evidencecheck.generation.providers import make_provider  # noqa: E402


def settings() -> Settings:
    cur = st.session_state.get("settings")
    if cur is None or not hasattr(cur, "llm_provider"):  # stale object from an older version
        st.session_state.settings = Settings()
    return st.session_state.settings


def sample_docs() -> list[dict]:
    return load_documents(DATA_RAW)


def corpus_docs() -> list[dict]:
    """Selected sample docs + user uploads (uploads live only in this session)."""
    docs = sample_docs()
    sel = st.session_state.get("sample_sel")
    if sel is not None:
        docs = [d for d in docs if d["source"] in sel]
    return docs + st.session_state.get("uploads", [])


@st.cache_resource(show_spinner="Loading embedding model…")
def get_embedder():
    if os.getenv("EC_EMBEDDER") == "hash":  # offline test hook only (lexical, not semantic)
        from evidencecheck.retrieval.embeddings import HashEmbedder
        return HashEmbedder()
    try:
        from evidencecheck.retrieval.embeddings import SentenceTransformerEmbedder
        return SentenceTransformerEmbedder(Settings().embedding_model)
    except Exception:
        return None


@st.cache_resource(show_spinner="Building index…")
def _build(docs: tuple, chunk_size: int, overlap: int):
    emb = get_embedder()
    if emb is None or not docs:
        return None
    recs = [dict(zip(("document_id", "source", "page", "text"), d)) for d in docs]
    return Retriever(chunk_documents(recs, chunk_size, overlap), emb)


def get_retriever():
    s = settings()
    docs = tuple((d["document_id"], d["source"], d["page"], d["text"]) for d in corpus_docs())
    return _build(docs, s.chunk_size, s.chunk_overlap)


def sample_retriever():
    """Index over the bundled sample docs only (used for gold-label evaluation)."""
    s = settings()
    docs = tuple((d["document_id"], d["source"], d["page"], d["text"]) for d in sample_docs())
    return _build(docs, s.chunk_size, s.chunk_overlap)


def provider():
    s = settings()
    return make_provider(s, api_key=st.session_state.get(f"key_{s.llm_provider}") or None)
