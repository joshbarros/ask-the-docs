from __future__ import annotations

import math

import httpx

from app.config import settings


def _normalize(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / n for x in v]


def embed(texts: list[str]) -> list[list[float]] | None:
    """Embed a batch via OpenRouter's OpenAI-compatible /embeddings endpoint.

    Returns None on any failure so retrieval degrades to lexical (BM25).
    """
    if not settings.openrouter_api_key:
        return None
    texts = [t for t in texts if t and t.strip()]
    if not texts:
        return None
    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(
                f"{settings.openrouter_base}/embeddings",
                headers={"authorization": f"Bearer {settings.openrouter_api_key}", "content-type": "application/json"},
                json={"model": settings.embedding_model, "input": texts},
            )
            resp.raise_for_status()
            data = resp.json()
        rows = sorted(data["data"], key=lambda d: d["index"])
        return [_normalize(list(d["embedding"])) for d in rows]
    except Exception:  # noqa: BLE001 - embeddings are an enhancement, not a hard dep
        return None
