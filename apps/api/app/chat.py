from __future__ import annotations

import httpx

from app.config import settings
from app.retrieve import retriever

SYSTEM = (
    "You are 'Ask the Docs', a grounded Q&A assistant. Answer ONLY from the provided context. "
    "Cite every claim with the [id] of the chunk that supports it, e.g. '... [rag:2]'. "
    "If the context does not contain the answer, say so explicitly. Keep answers concise."
)


def _fallback(question: str, hits: list[dict]) -> dict:
    if not hits:
        return {"answer": "No relevant document found for that question.", "sources": [], "mode": "fallback"}
    return {
        "answer": hits[0]["text"],
        "sources": [{"id": h["id"], "source": h["source"]} for h in hits],
        "mode": "fallback",
    }


async def answer(question: str) -> dict:
    hits = retriever.search(question, k=4)
    if not settings.llm_enabled:
        return _fallback(question, hits)

    ctx = "\n\n".join(f"[{h['id']}] (source: {h['source']})\n{h['text']}" for h in hits)
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {question}"},
    ]
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{settings.openrouter_base}/chat/completions",
                headers={
                    "authorization": f"Bearer {settings.openrouter_api_key}",
                    "content-type": "application/json",
                },
                json={"model": settings.openrouter_model, "messages": messages, "temperature": 0.2, "max_tokens": 500},
            )
            resp.raise_for_status()
            data = resp.json()
        reply = data["choices"][0]["message"]["content"]
        return {
            "answer": reply,
            "sources": [{"id": h["id"], "source": h["source"]} for h in hits],
            "mode": "llm",
            "model": settings.openrouter_model,
        }
    except Exception as exc:  # noqa: BLE001 - degrade gracefully, never break the UI
        return {
            "answer": f"{_fallback(question, hits)['answer']}\n\n(LLM unavailable: {type(exc).__name__})",
            "sources": [{"id": h["id"], "source": h["source"]} for h in hits],
            "mode": "fallback",
        }
