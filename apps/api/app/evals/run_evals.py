"""Retrieval eval gate for Ask the Docs.

Runs offline (no model needed). A case passes when every `must_include` substring
appears in the top-k retrieved context. Exit non-zero below the gate -> wire into CI.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.retrieve import retriever

HERE = Path(__file__).parent
EVALSET = HERE / "evalset.jsonl"
RESULTS = HERE / "results.json"
GATE = 0.8
K = 4


def main() -> int:
    cases = [json.loads(line) for line in EVALSET.read_text(encoding="utf-8").splitlines() if line.strip()]
    rows = []
    for case in cases:
        hits = retriever.search(case["question"], k=K)
        combined = " ".join(h["text"] for h in hits).lower()
        missing = [kw for kw in case["must_include"] if kw.lower() not in combined]
        passed = not missing
        rows.append(
            {
                "id": case["id"],
                "passed": passed,
                "missing": missing,
                "top_source": hits[0]["source"] if hits else None,
                "score": hits[0]["score"] if hits else 0,
            }
        )

    passed = sum(1 for r in rows if r["passed"])
    total = len(rows)
    rate = passed / total if total else 0.0

    print(f"\n  retrieval evals · {total} cases (k={K})\n")
    print(f"  {'CASE':<16}{'RESULT'}")
    print(f"  {'-'*30}")
    for r in rows:
        verdict = "PASS" if r["passed"] else f"FAIL missing={r['missing']}"
        print(f"  {r['id']:<16}{verdict}")
    gate = "PASS" if rate >= GATE else "FAIL"
    print(f"\n  score {passed}/{total} = {rate:.0%} · gate {GATE:.0%} → {gate}\n")

    RESULTS.write_text(json.dumps({"total": total, "passed": passed, "rate": round(rate, 3), "gate_ok": rate >= GATE, "cases": rows}, indent=2), encoding="utf-8")
    return 0 if rate >= GATE else 1


if __name__ == "__main__":
    raise SystemExit(main())
