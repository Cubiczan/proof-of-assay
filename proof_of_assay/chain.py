"""SHA-256 hash chain for audit receipts.

Chain layout (11 entries for the 8-lot fixture):
  0 GENESIS, 1-8 LOT_AUDIT (one per lot), 9 SUMMARY, 10 ANCHOR_PLACEHOLDER
Each entry hash = sha256(prev_hash + canonical_json(index,type,payload)).
Tampering with any payload breaks verification -> FAIL.
"""
from __future__ import annotations
import hashlib, json

def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def _hash(prev, index, typ, payload):
    return hashlib.sha256(f"{prev}|{index}|{typ}|{_canonical(payload)}".encode()).hexdigest()

def build_chain(results):
    entries = []
    def add(typ, payload):
        idx = len(entries)
        prev = entries[-1]["hash"] if entries else "0" * 64
        entries.append({"index": idx, "type": typ, "payload": payload, "prev_hash": prev,
                        "hash": _hash(prev, idx, typ, payload)})
    add("GENESIS", {"project": "Proof-of-Assay", "mode": results["mode"], "dataset": results["dataset"]})
    for d in results["decisions"]:
        add("LOT_AUDIT", d)
    add("SUMMARY", {"total_lots": results["total_lots"], "clean_count": results["clean_count"],
                    "exception_count": results["exception_count"], "cash_at_risk_usd": results["cash_at_risk_usd"]})
    add("ANCHOR_PLACEHOLDER", {"arweave": results["arweave"], "note": "Anchor only after approved live Nosana/Arweave run; do not claim a tx in fixture mode."})
    return entries

def verify_chain(entries):
    prev = "0" * 64
    for i, e in enumerate(entries):
        if e.get("index") != i or e.get("prev_hash") != prev:
            return False
        if e.get("hash") != _hash(prev, i, e.get("type"), e.get("payload")):
            return False
        prev = e["hash"]
    return True
