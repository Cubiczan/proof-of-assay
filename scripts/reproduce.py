#!/usr/bin/env python3
"""Reproduce results.json from synthetic fixtures (deterministic, no network)."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from proof_of_assay import run_audit, build_chain

def main():
    results = run_audit()
    chain = build_chain(results)
    out = dict(results)
    out["chain"] = chain
    out["chain_length"] = len(chain)
    out["chain_head"] = chain[-1]["hash"] if chain else None
    dest = Path(__file__).resolve().parent.parent / "results.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"lots={results['total_lots']} clean={results['clean_count']} exceptions={results['exception_count']}")
    print(f"cash_at_risk_usd={results['cash_at_risk_usd']:.2f}")
    print(f"chain_entries={len(chain)} head={out['chain_head']}")
    print(f"wrote {dest}")

if __name__ == "__main__":
    main()
