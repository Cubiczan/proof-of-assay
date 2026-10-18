#!/usr/bin/env python3
"""Verify the hash chain in results.json. Exit 0 = PASS, 1 = FAIL.
Usage: python scripts/verify_chain.py [--tamper]  (--tamper demos FAIL detection)"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from proof_of_assay import verify_chain

def main():
    tamper = "--tamper" in sys.argv
    p = Path(__file__).resolve().parent.parent / "results.json"
    doc = json.loads(p.read_text())
    chain = doc["chain"]
    if tamper:
        chain = json.loads(json.dumps(chain))
        chain[3]["payload"]["invoiced_amount_usd"] = 1.00
        print("TAMPER DEMO: altered LOT_AUDIT payload at index 3")
    ok = verify_chain(chain)
    print(f"chain_length={len(chain)} verification={'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
