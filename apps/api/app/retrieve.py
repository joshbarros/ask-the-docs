from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data" / "docs"
_WORD = re.compile(r"[a-z0-9]+")


@dataclass
class Chunk:
    id: str
    source: str
    text: str


class Retriever:
    """Chunking + a BM25 index (no external deps). Deterministic and cheap.

    Production note: this is the lexical half of hybrid search. Swap in a vector
    store (pgvector / FAISS) behind the same `search()` interface for semantic recall.
    """

    def __init__(self, docs_dir: Path = DATA_DIR, chunk_size: int = 500, overlap: int = 80):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.chunks: list[Chunk] = []
        self._tok: list[list[str]] = []
        self._df: dict[str, int] = {}
        self._n = 0
        self._load(docs_dir)
        self._build()

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return _WORD.findall(text.lower())

    def _chunk(self, text: str) -> list[str]:
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return []
        parts: list[str] = []
        i = 0
        n = len(text)
        while i < n:
            parts.append(text[i : i + self.chunk_size])
            if i + self.chunk_size >= n:
                break
            i += self.chunk_size - self.overlap
        return parts

    def _load(self, docs_dir: Path) -> None:
        if not docs_dir.exists():
            return
        for p in sorted(docs_dir.glob("*.md")):
            txt = p.read_text(encoding="utf-8")
            for j, part in enumerate(self._chunk(txt)):
                self.chunks.append(Chunk(id=f"{p.stem}:{j}", source=p.name, text=part))

    def _build(self) -> None:
        self._tok = [self._tokens(c.text) for c in self.chunks]
        self._n = len(self._tok)
        self._df = {}
        for toks in self._tok:
            for t in set(toks):
                self._df[t] = self._df.get(t, 0) + 1

    def add(self, title: str, text: str) -> None:
        safe = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "doc"
        for j, part in enumerate(self._chunk(text)):
            self.chunks.append(Chunk(id=f"{safe}:{j}", source=title, text=part))
        self._build()

    def search(self, query: str, k: int = 4) -> list[dict]:
        q = self._tokens(query)
        if not q or not self.chunks:
            return []
        avgdl = sum(len(t) for t in self._tok) / max(self._n, 1)
        k1, b = 1.5, 0.75
        scored: list[tuple[float, int]] = []
        for i, toks in enumerate(self._tok):
            dl = len(toks)
            s = 0.0
            for term in q:
                tf = toks.count(term)
                if not tf:
                    continue
                idf = math.log(1 + (self._n - self._df.get(term, 0) + 0.5) / (self._df.get(term, 0) + 0.5))
                s += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl))
            if s > 0:
                scored.append((s, i))
        scored.sort(reverse=True)
        out: list[dict] = []
        for s, i in scored[:k]:
            c = self.chunks[i]
            out.append({"id": c.id, "source": c.source, "score": round(s, 3), "text": c.text})
        return out


retriever = Retriever()
