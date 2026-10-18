"""Deterministic reconciliation for synthetic mining-payables fixtures.

Rules (no LLM required to reproduce):
  expected_amount = tonnes * contracted_price_usd_per_tonne
  variance = invoiced_amount - expected_amount
  A lot is an EXCEPTION if |variance| > $0.01, invoice grade != assay grade,
  or invoiced tonnes != contracted tonnes. Cash at risk is the sum of
  positive variances on exception lots.
All data is synthetic fixture data. Inference mode is FIXTURE/LOCAL:
no live Nosana deployment and no live Arweave anchor are claimed.
"""
from __future__ import annotations
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "fixtures.json"

def load_fixtures(path=None):
    p = Path(path) if path else DATA
    doc = json.loads(p.read_text())
    return doc["lots"]

def expected_amount(lot):
    return round(lot["tonnes"] * lot["contracted_price_usd_per_tonne"], 2)

def audit_lot(lot):
    exp = expected_amount(lot)
    invoiced = round(float(lot["invoiced_amount_usd"]), 2)
    variance = round(invoiced - exp, 2)
    reasons = []
    if abs(variance) > 0.01:
        reasons.append(f"Invoiced ${invoiced:,.2f} != expected ${exp:,.2f} (variance ${variance:,.2f})")
    if lot.get("invoice_grade_gpt") != lot.get("assay_grade_gpt"):
        reasons.append(f"Grade mismatch: invoice {lot.get('invoice_grade_gpt')} g/t vs assay {lot.get('assay_grade_gpt')} g/t")
    if lot.get("invoiced_tonnes") != lot.get("tonnes"):
        reasons.append(f"Quantity mismatch: invoiced {lot.get('invoiced_tonnes')} t vs contracted {lot.get('tonnes')} t")
    status = "EXCEPTION" if reasons else "CLEAN"
    return {
        "lot_id": lot["lot_id"], "supplier": lot["supplier"], "material": lot["material"],
        "tonnes": lot["tonnes"], "expected_amount_usd": exp, "invoiced_amount_usd": invoiced,
        "variance_usd": variance, "status": status, "reasons": reasons,
        "cash_at_risk_usd": variance if (status == "EXCEPTION" and variance > 0) else 0.0,
    }

def run_audit(lots=None):
    lots = lots if lots is not None else load_fixtures()
    decisions = [audit_lot(l) for l in lots]
    exceptions = [d for d in decisions if d["status"] == "EXCEPTION"]
    return {
        "mode": "FIXTURE/LOCAL",
        "inference": "deterministic-rules (no live Nosana deployment claimed)",
        "arweave": "NOT_ANCHORED (fixture mode; no live anchor claimed)",
        "model_planned": "Qwen/Qwen2.5-1.5B-Instruct via vLLM on Nosana (see nosana/proof-of-assay-vllm.json)",
        "dataset": "SYNTHETIC FIXTURE - 8 lots",
        "total_lots": len(decisions),
        "clean_count": len(decisions) - len(exceptions),
        "exception_count": len(exceptions),
        "cash_at_risk_usd": round(sum(d["cash_at_risk_usd"] for d in decisions), 2),
        "decisions": decisions,
    }
