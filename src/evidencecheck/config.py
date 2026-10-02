"""Central configuration (environment + defaults)."""
from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # pragma: no cover
    pass

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
EVAL_DIR = ROOT / "data" / "evaluation"
RESULTS = ROOT / "results"


@dataclass
class Settings:
    """Project-defined experimental settings (thresholds are NOT validated constants)."""
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k: int = 3
    supported_threshold: float = 0.75
    partial_threshold: float = 0.55
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "gemini").lower())
    groq_model: str = field(default_factory=lambda: os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"))
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"))


def env_file() -> Path:
    return ROOT / ".env"


def _key_from_file(path: Path, var: str) -> str:
    """Read a variable from a .env file; tolerates UTF-8 BOM and UTF-16 (Windows)."""
    try:
        from dotenv import dotenv_values
    except ImportError:
        return ""
    for enc in ("utf-8-sig", "utf-16"):
        try:
            v = dotenv_values(path, encoding=enc).get(var) or ""
            if v.strip():
                return v
        except Exception:
            continue
    return ""


def api_key(var: str) -> str:
    """Key from .env (re-read each call), then env var, then Streamlit secrets."""
    key = ""
    for p in (env_file(), Path.cwd() / ".env"):
        if p.is_file():
            key = _key_from_file(p, var)
            if key:
                break
    key = (key or os.getenv(var, "")).strip().strip("\"'")
    if key:
        return key
    try:
        import streamlit as st
        return str(st.secrets.get(var, "")).strip()
    except Exception:
        return ""


def groq_api_key() -> str:
    return api_key("GROQ_API_KEY")


def gemini_api_key() -> str:
    return api_key("GEMINI_API_KEY") or api_key("GOOGLE_API_KEY")
