from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.chat import answer
from app.config import settings
from app.retrieve import retriever

app = FastAPI(title="Ask the Docs", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class IngestRequest(BaseModel):
    title: str
    text: str


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "llm": settings.llm_enabled,
        "model": settings.openrouter_model,
        "chunks": len(retriever.chunks),
    }


@app.get("/docs")
def docs() -> dict:
    return {"sources": sorted({c.source for c in retriever.chunks}), "chunks": len(retriever.chunks)}


@app.post("/ingest")
def ingest(req: IngestRequest) -> dict:
    retriever.add(req.title, req.text)
    return {"ok": True, "chunks": len(retriever.chunks)}


@app.post("/chat")
async def chat(req: ChatRequest) -> dict:
    return await answer(req.question)
