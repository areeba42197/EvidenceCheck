from __future__ import annotations
import time
import requests
from ..config import groq_api_key, gemini_api_key

# Tried in order if the configured model is retired (checked against Groq's deprecation page, Oct 2026).
FALLBACK_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]


class LLMProvider:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class ProviderError(RuntimeError):
    """User-presentable provider failure (never contains the API key)."""


class GroqProvider(LLMProvider):
    URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, model: str, api_key: str | None = None, retries: int = 3):
        self.model, self.retries = model, retries
        self.api_key = (api_key if api_key is not None else groq_api_key()).strip().strip("\"'")
        self.active_model = model

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _post(self, model: str, prompt: str) -> requests.Response:
        body = {"model": model, "temperature": 0, "messages": [{"role": "user", "content": prompt}]}
        for attempt in range(self.retries):
            try:
                r = requests.post(self.URL, json=body, timeout=90,
                                  headers={"Authorization": f"Bearer {self.api_key}"})
            except requests.RequestException:
                raise ProviderError("The Groq API could not be reached.")
            if r.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            return r
        raise ProviderError("Groq rate limit reached. Try again shortly.")

    def generate(self, prompt: str) -> str:
        if not self.configured:
            raise ProviderError("Groq API key not configured. Retrieval and offline evaluation are still available.")
        last = ""
        for model in dict.fromkeys([self.model, *FALLBACK_MODELS]):
            r = self._post(model, prompt)
            if r.status_code == 200:
                self.active_model = model
                return (r.json()["choices"][0]["message"].get("content") or "").strip()
            if r.status_code == 401:
                raise ProviderError("Groq rejected the API key (HTTP 401). Create a new key at console.groq.com.")
            try:
                last = r.json()["error"]["message"][:200]
            except Exception:
                last = ""
            if r.status_code in (400, 404):   # retired/unknown model -> try next
                continue
            raise ProviderError(f"Groq API returned HTTP {r.status_code}. {last}")
        raise ProviderError(f"No available Groq model worked. Last error: {last}")


# Tried in order if the configured Gemini model is retired/unknown.
GEMINI_FALLBACKS = ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-2.5-flash"]


class GeminiProvider(LLMProvider):
    """Google Gemini API (native generateContent). Free tier: Flash / Flash-Lite models only."""
    URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, model: str, api_key: str | None = None, retries: int = 3):
        self.model, self.retries = model, retries
        self.api_key = (api_key if api_key is not None else gemini_api_key()).strip().strip("\"'")
        self.active_model = model

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def _post(self, model: str, prompt: str) -> requests.Response:
        body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0}}
        for attempt in range(self.retries):
            try:
                r = requests.post(self.URL.format(model=model), json=body, timeout=90,
                                  headers={"x-goog-api-key": self.api_key})
            except requests.RequestException:
                raise ProviderError("The Gemini API could not be reached.")
            if r.status_code == 429:
                time.sleep(4 * (attempt + 1))
                continue
            return r
        raise ProviderError("Gemini free-tier rate limit reached (requests per minute/day). Wait and retry.")

    def generate(self, prompt: str) -> str:
        if not self.configured:
            raise ProviderError("Gemini API key not configured. Retrieval and offline evaluation are still available.")
        last = ""
        for model in dict.fromkeys([self.model, *GEMINI_FALLBACKS]):
            r = self._post(model, prompt)
            if r.status_code == 200:
                self.active_model = model
                parts = (r.json().get("candidates") or [{}])[0].get("content", {}).get("parts", [])
                return "".join(p.get("text", "") for p in parts).strip()
            try:
                last = r.json()["error"]["message"][:200]
            except Exception:
                last = ""
            if r.status_code in (400, 403) and "API key" in last:
                raise ProviderError("Gemini rejected the API key. Create one at aistudio.google.com/apikey.")
            if r.status_code == 404:
                continue
            raise ProviderError(f"Gemini API returned HTTP {r.status_code}. {last}")
        raise ProviderError(f"No available Gemini model worked. Last error: {last}")


def make_provider(settings, api_key: str | None = None) -> LLMProvider:
    """Build the provider chosen in Settings ('gemini' or 'groq')."""
    if settings.llm_provider == "groq":
        return GroqProvider(settings.groq_model, api_key=api_key)
    return GeminiProvider(settings.gemini_model, api_key=api_key)
