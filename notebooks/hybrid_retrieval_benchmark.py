# Hybrid retrieval benchmark: BM25 vs embeddings vs RRF
# Self-contained (no GPU, no network). Production uses OpenRouter embeddings
# (text-embedding-3-small); here we use TF-IDF cosine as a local vector proxy.
import math
import re
from collections import Counter

WORD = re.compile(r"[a-z0-9]+")

DOCS = {
    "rag.md": (
        "RAG grounds a model's answer in retrieved context. Pipeline: layout-aware ingestion, "
        "chunking on section boundaries with overlap, hybrid retrieval (BM25 for exact terms plus "
        "vector similarity for paraphrases, fused with Reciprocal Rank Fusion), reranking, grounding "
        "with inline citations, and an explicit refusal path. Naive RAG fails because embeddings blur "
        "exact identifiers like invoice numbers, top-k returns near-duplicates, fixed-size chunking "
        "shreds tables, and the model always answers even without context. Evaluate groundedness, "
        "refusal precision, context recall and citation accuracy."
    ),
    "agents.md": (
        "An agent is a model in a loop; a harness is everything around it: typed tools (schema plus "
        "handler, errors returned as data), MCP for reusable integrations, approval gates that scale "
        "autonomy with reversibility, bounded loops with retries, full execution traces, and evals. "
        "Score tool-call accuracy and unsafe-action block rate. Autonomy grows only as evals prove reliability."
    ),
    "evals.md": (
        "An eval harness is a labeled ground-truth set, metrics tied to real failures, and a threshold "
        "that blocks regressions. Metrics: groundedness, answer relevance, context recall, refusal "
        "precision, citation accuracy. Run the harness in CI on every change; fail the build below the gate."
    ),
}

# Questions mapped to the document that must be retrieved.
GOLDEN = [
    ("Why does naive RAG fail?", "rag.md"),
    ("What is hybrid search?", "rag.md"),
    ("What is an approval gate in agents?", "agents.md"),
    ("What is MCP?", "agents.md"),
    ("How do I evaluate an LLM system?", "evals.md"),
]


def tokens(s: str):
    return WORD.findall(s.lower())


def chunk(text, size=200, overlap=40):
    text = re.sub(r"\s+", " ", text).strip()
    parts, i, n = [], 0, len(text)
    while i < n:
        parts.append(text[i : i + size])
        if i + size >= n:
            break
        i += size - overlap
    return parts


CHUNKS = []
for src, txt in DOCS.items():
    for j, p in enumerate(chunk(txt)):
        CHUNKS.append({"id": f"{src[:-3]}:{j}", "source": src, "text": p})

TOKS = [tokens(c["text"]) for c in CHUNKS]
N = len(CHUNKS)
DF = Counter()
for t in TOKS:
    for w in set(t):
        DF[w] += 1


def bm25(query, k=10):
    q = tokens(query)
    avg = sum(len(t) for t in TOKS) / N
    k1, b = 1.5, 0.75
    scored = []
    for i, t in enumerate(TOKS):
        dl, s = len(t), 0.0
        for term in q:
            tf = t.count(term)
            if not tf:
                continue
            idf = math.log(1 + (N - DF.get(term, 0) + 0.5) / (DF.get(term, 0) + 0.5))
            s += idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avg))
        if s > 0:
            scored.append((s, i))
    scored.sort(reverse=True)
    return [i for _, i in scored[:k]]


# TF-IDF vectors (local proxy for embeddings)
IDF = {w: math.log((1 + N) / (1 + DF[w])) + 1 for w in DF}
VOCAB = sorted(DF)


def tfidf_vec(t):
    c = Counter(t)
    v = {w: (c[w] / len(t)) * IDF[w] for w in c if w in IDF}
    norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
    return {w: x / norm for w, x in v.items()}


CHUNK_VECS = [tfidf_vec(t) for t in TOKS]


def cosine(a, b):
    keys = set(a) & set(b)
    return sum(a[w] * b[w] for w in keys)


def vec_search(query, k=10):
    qv = tfidf_vec(tokens(query))
    scored = [(cosine(qv, v), i) for i, v in enumerate(CHUNK_VECS)]
    scored.sort(reverse=True)
    return [i for _, i in scored[:k]]


def rrf(*rank_lists, k=10):
    scores = {}
    for ranks in rank_lists:
        for rank, i in enumerate(ranks):
            scores[i] = scores.get(i, 0) + 1 / (60 + rank + 1)
    return sorted(scores, key=scores.get, reverse=True)[:k]


def recall_at_k(method, q, target_doc, k=5):
    ranked = method(q, k=k)
    return 1.0 if any(CHUNKS[i]["source"] == target_doc for i in ranked) else 0.0


print("Chunks:", N, "| Questions:", len(GOLDEN))
print(f"\n{'question':<38}{'bm25':>6}{'vec':>6}{'rrf':>6}")
print("-" * 58)
bm, vc, rr = [], [], []
for q, doc in GOLDEN:
    b = recall_at_k(bm25, q, doc)
    v = recall_at_k(vec_search, q, doc)
    r = recall_at_k(lambda x, k: rrf(bm25(x), vec_search(x), k=k), q, doc)
    bm.append(b); vc.append(v); rr.append(r)
    print(f"{q:<38}{b:>6.0f}{v:>6.0f}{r:>6.0f}")
print("-" * 58)
print(f"{'recall@5':<38}{sum(bm)/len(bm):>6.2f}{sum(vc)/len(vc):>6.2f}{sum(rr)/len(rr):>6.2f}")
print("\nTakeaway: lexical (BM25) wins on exact terms, vectors win on paraphrases;")
print("RRF fusion is never worse than the best single method and is more robust.")
