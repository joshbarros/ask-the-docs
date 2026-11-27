export const runtime = "nodejs";

const API_URL = process.env.API_URL || "http://localhost:8000";

export async function POST(req: Request) {
  const body = await req.json().catch(() => ({}));
  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30000),
    });
    const data = await res.json();
    return Response.json(data);
  } catch (e) {
    return Response.json(
      { answer: `API unavailable (${(e as Error).message}). Try again.`, sources: [], mode: "fallback" },
      { status: 200 }
    );
  }
}
