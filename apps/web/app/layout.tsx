import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ask the Docs — grounded answers over your documents",
  description:
    "Production RAG demo: hybrid retrieval, inline citations and an eval gate. Ask anything about the indexed docs.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
