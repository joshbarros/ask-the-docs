"use client";

import { useState } from "react";
import "./globals.css";

type Source = { id: string; source: string };
type Message = { role: "user" | "assistant"; text: string; sources?: Source[]; mode?: string };

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const suggestions = [
  "Why does naive RAG fail?",
  "What is hybrid search?",
  "What is an approval gate in agents?",
  "How do I evaluate an LLM system?",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask(q: string) {
    const question = q.trim();
    if (!question || loading) return;
    setMessages((m) => [...m, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", text: data.answer, sources: data.sources, mode: data.mode }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: `Error: ${(e as Error).message}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 760, margin: "0 auto", padding: "48px 20px" }}>
      <header style={{ marginBottom: 24 }}>
        <div style={{ fontSize: 12, letterSpacing: 2, textTransform: "uppercase", color: "#8a93a6" }}>
          Production RAG · hybrid retrieval · evals
        </div>
        <h1 style={{ fontSize: 32, margin: "8px 0 4px" }}>
          Ask the Docs <span style={{ color: "#7c5cff" }}>—</span> grounded answers with citations
        </h1>
        <p style={{ color: "#8a93a6", margin: 0 }}>
          Ask anything about the indexed docs. Answers cite the exact chunks that support them.
        </p>
      </header>

      <div
        style={{
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 16,
          background: "rgba(255,255,255,0.03)",
          padding: 20,
          minHeight: 300,
        }}
      >
        {messages.length === 0 ? (
          <div>
            <div style={{ color: "#8a93a6", fontSize: 13, marginBottom: 12 }}>Try one:</div>
            {suggestions.map((s) => (
              <button
                key={s}
                onClick={() => ask(s)}
                style={{
                  display: "block",
                  marginBottom: 8,
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  color: "#e8ecf5",
                  borderRadius: 999,
                  padding: "8px 14px",
                  cursor: "pointer",
                }}
              >
                {s}
              </button>
            ))}
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 12, color: "#8a93a6", marginBottom: 4 }}>
                {m.role === "user" ? "You" : "Assistant"}
                {m.mode === "llm" ? " · llm" : m.mode === "fallback" ? " · fallback" : ""}
              </div>
              <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.6 }}>{m.text}</div>
              {m.sources?.length ? (
                <div style={{ marginTop: 8, display: "flex", flexWrap: "wrap", gap: 6 }}>
                  {m.sources.map((s) => (
                    <span
                      key={s.id}
                      style={{
                        fontSize: 11,
                        fontFamily: "monospace",
                        background: "rgba(34,211,238,0.08)",
                        color: "#22d3ee",
                        borderRadius: 6,
                        padding: "2px 8px",
                      }}
                    >
                      {s.id}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          ))
        )}
        {loading ? <div style={{ color: "#8a93a6", fontSize: 13 }}>Thinking…</div> : null}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
        style={{ display: "flex", gap: 8, marginTop: 16 }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the docs…"
          style={{
            flex: 1,
            background: "#0a0c14",
            border: "1px solid rgba(255,255,255,0.1)",
            color: "#e8ecf5",
            borderRadius: 12,
            padding: "12px 16px",
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            background: "#e8ecf5",
            color: "#05060a",
            border: "none",
            borderRadius: 12,
            padding: "12px 20px",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          Send
        </button>
      </form>
    </main>
  );
}
