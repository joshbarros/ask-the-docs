# Ask the Docs

Production RAG over a document corpus — hybrid retrieval, inline citations and an eval gate.
Built as an NX monorepo. Live demo of what "grounded answers" actually means.

![license](https://img.shields.io/badge/license-MIT-blue)
![demo](https://img.shields.io/badge/demo-live-brightgreen)
![CI](https://github.com/joshbarros/ask-the-docs/actions/workflows/deploy.yml/badge.svg)
![python](https://img.shields.io/badge/python-3.12-blue)

## Stack
- `apps/api` — FastAPI: chunking + BM25 retrieval, grounded answers via **OpenRouter** (`deepseek/deepseek-chat`), offline eval gate.
- `apps/web` — Next.js chat UI with clickable citations.
- NX monorepo (`nx run api:serve`, `nx run web:serve`, `nx run api:test`).

## Run locally
```bash
pnpm install
cp .env.example .env   # add OPENROUTER_API_KEY
pnpm nx run api:serve      # http://localhost:8000
pnpm nx run web:serve      # http://localhost:3000
pnpm nx run api:test       # retrieval evals (gate 80%)
```

## API
- `GET  /health` — status + whether the LLM is on.
- `GET  /docs`  — indexed sources + chunk count.
- `POST /ingest` `{title, text}` — add a document to the index.
- `POST /chat` `{question}` → `{answer, sources[], mode, model}`.

## Deploy (Render)
Blueprint: `render.yaml` deploys `api` and `web` as Docker services.
Set `OPENROUTER_API_KEY` in the Render dashboard, and `NEXT_PUBLIC_API_URL`
on the web service to the API's public URL.

## Eval gate
`apps/api/app/evals/run_evals.py` scores retrieval against `evalset.jsonl`
(substring recall over top-k context). Exit non-zero below the gate → wire into CI.
