from __future__ import annotations
from .providers import LLMProvider

RAG_PROMPT = """You are an evidence-grounded research assistant.

Answer the user's question using ONLY the supplied evidence.
Do not introduce facts that are not supported by the evidence.
If the evidence is insufficient, say that the available evidence is insufficient.

Retrieved evidence:

{evidence}

Question:
{question}

Provide a concise factual answer."""


def build_rag_prompt(question: str, evidence: list[dict]) -> str:
    ev = "\n\n".join(f"[EVIDENCE_{i+1}]\n{e['text']}" for i, e in enumerate(evidence))
    return RAG_PROMPT.format(evidence=ev, question=question)


def direct_answer(question: str, provider: LLMProvider) -> str:
    return provider.generate(f"Answer concisely and factually.\n\nQuestion:\n{question}")


def rag_answer(question: str, retriever, provider: LLMProvider, top_k: int = 3) -> tuple[str, list[dict]]:
    ev = retriever.retrieve(question, top_k)
    if not ev:
        return "", []
    return provider.generate(build_rag_prompt(question, ev)), ev
