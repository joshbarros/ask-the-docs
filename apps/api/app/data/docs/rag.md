# Retrieval-Augmented Generation in production

RAG is the pattern of grounding a language model's answer in a retrieved corpus. It exists because a model alone hallucinates: it will answer confidently even when the information is not in its weights.

## The pipeline

1. **Ingestion.** Parse documents with layout awareness. For PDFs keep tables and reading order; OCR only pages that need it. Store each chunk with metadata: document, page, section.
2. **Chunking.** Split on section boundaries rather than a fixed token count. Overlap chunks (typically 10-20%) so context does not cut a thought in half.
3. **Retrieval.** Use hybrid search: lexical (BM25 or full-text) for exact terms, IDs and numbers, plus vector similarity for paraphrases. Fuse with Reciprocal Rank Fusion.
4. **Reranking.** Take the top ~30 candidates and rerank with a cross-encoder to the top 3-5. This is the single highest-leverage quality step per dollar.
5. **Grounding.** Force the model to answer only from the retrieved passages, with inline citations, and verify each citation supports its claim.
6. **Refusal.** If retrieval confidence is low, return a clear "I don't have enough to answer that" plus the closest sources.

## Why naive RAG fails

- Exact identifiers vanish: embeddings blur invoice numbers and error codes that lexical search preserves.
- Top-k returns near-duplicates of one passage, crowding out the one that matters.
- Fixed-size chunking shreds tables and code.
- The model always answers, even with no context. Refusal precision is a metric, not an afterthought.

## Evaluation

Measure groundedness (is the answer supported by the retrieved context), refusal precision (does it decline when it should), context recall (did retrieval find the right passage), and citation accuracy. Gate every deploy on these numbers, not on vibe checks.
