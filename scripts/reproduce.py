#!/usr/bin/env python3
"""Reproduce results.json from synthetic fixtures (deterministic, no network).

Pass --explain to also call a Nosana (or other OpenAI-compatible) endpoint
for short exception narratives. That path requires NOSANA_LLM_BASE_URL and
is skipped cleanly when it is unset. Narratives are written under
`narration` / `decisions[].narrative` only — they are not hashed into the
chain, so the fixture chain head stays stable.
"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from proof_of_assay import attach_narratives, run_audit, build_chain

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Attach optional LLM narratives when NOSANA_LLM_BASE_URL is set",
    )
    args = parser.parse_args()
    results = run_audit()
    chain = build_chain(results)
    out = dict(results)
    if args.explain:
        narrated = attach_narratives(results)
        out["decisions"] = narrated["decisions"]
        out["narration"] = narrated.get("narration")
    out["chain"] = chain
    out["chain_length"] = len(chain)
    out["chain_head"] = chain[-1]["hash"] if chain else None
    dest = Path(__file__).resolve().parent.parent / "results.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"lots={results['total_lots']} clean={results['clean_count']} exceptions={results['exception_count']}")
    print(f"cash_at_risk_usd={results['cash_at_risk_usd']:.2f}")
    print(f"chain_entries={len(chain)} head={out['chain_head']}")
    if args.explain:
        n = out.get("narration") or {}
        print(f"narration={n.get('status')} explained={n.get('explained', 0)} failed={n.get('failed', 0)}")
    print(f"wrote {dest}")

if __name__ == "__main__":
    main()
