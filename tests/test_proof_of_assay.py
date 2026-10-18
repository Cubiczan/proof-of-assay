import copy, json
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT))
from proof_of_assay import run_audit, build_chain, verify_chain, load_fixtures, audit_lot

@pytest.fixture(scope="module")
def results():
    return run_audit()

@pytest.fixture(scope="module")
def chain(results):
    return build_chain(results)

def by_id(results, lot_id):
    return next(d for d in results["decisions"] if d["lot_id"] == lot_id)

# 1-5: headline numbers
def test_load_fixtures_returns_eight():
    assert len(load_fixtures()) == 8

def test_total_lots(results):
    assert results["total_lots"] == 8

def test_clean_count_five(results):
    assert results["clean_count"] == 5

def test_exception_count_three(results):
    assert results["exception_count"] == 3

def test_cash_at_risk_exact(results):
    assert results["cash_at_risk_usd"] == 289849.19

# 6-10: clean lots
@pytest.mark.parametrize("lot_id", ["LOT-001", "LOT-002", "LOT-004", "LOT-005", "LOT-008"])
def test_clean_lots_have_zero_variance(results, lot_id):
    d = by_id(results, lot_id)
    assert d["status"] == "CLEAN" and d["variance_usd"] == 0.0 and d["cash_at_risk_usd"] == 0.0

# 11-13: exception lots flagged
@pytest.mark.parametrize("lot_id", ["LOT-003", "LOT-006", "LOT-007"])
def test_exception_lots_flagged(results, lot_id):
    assert by_id(results, lot_id)["status"] == "EXCEPTION"

# 14-16: exception cash values
@pytest.mark.parametrize("lot_id,amount", [("LOT-003", 132480.50), ("LOT-006", 98215.44), ("LOT-007", 59153.25)])
def test_exception_cash_values(results, lot_id, amount):
    assert by_id(results, lot_id)["cash_at_risk_usd"] == amount

# 17-35: rules, chain, honesty badges
def test_expected_amount_formula():
    lot = load_fixtures()[0]
    assert audit_lot(lot)["expected_amount_usd"] == round(lot["tonnes"] * lot["contracted_price_usd_per_tonne"], 2)

def test_grade_mismatch_reason(results):
    assert any("Grade mismatch" in r for r in by_id(results, "LOT-003")["reasons"])

def test_quantity_mismatch_reason(results):
    assert any("Quantity mismatch" in r for r in by_id(results, "LOT-006")["reasons"])

def test_price_variance_reason(results):
    assert any("Invoiced $" in r for r in by_id(results, "LOT-007")["reasons"])

def test_chain_length_11(chain):
    assert len(chain) == 11

def test_chain_genesis_type(chain):
    assert chain[0]["type"] == "GENESIS" and chain[0]["prev_hash"] == "0" * 64

def test_chain_summary_payload(chain):
    assert chain[9]["type"] == "SUMMARY" and chain[9]["payload"]["cash_at_risk_usd"] == 289849.19

def test_chain_anchor_placeholder_not_claimed(chain):
    assert chain[10]["type"] == "ANCHOR_PLACEHOLDER" and "NOT_ANCHORED" in chain[10]["payload"]["arweave"]

def test_verify_chain_pass(chain):
    assert verify_chain(chain) is True

def test_verify_chain_tamper_payload_fails(chain):
    bad = copy.deepcopy(chain); bad[3]["payload"]["invoiced_amount_usd"] = 1.00
    assert verify_chain(bad) is False

def test_verify_chain_tamper_prev_hash_fails(chain):
    bad = copy.deepcopy(chain); bad[5]["prev_hash"] = "f" * 64
    assert verify_chain(bad) is False

def test_chain_hashes_are_hex64(chain):
    assert all(len(e["hash"]) == 64 and all(c in "0123456789abcdef" for c in e["hash"]) for e in chain)

def test_chain_is_deterministic(results):
    assert build_chain(results) == build_chain(results)

def test_results_mode_fixture_local(results):
    assert results["mode"] == "FIXTURE/LOCAL"

def test_model_planned_is_qwen(results):
    assert "Qwen2.5-1.5B" in results["model_planned"]

def test_nosana_job_names_qwen():
    doc = json.loads((ROOT / "nosana/proof-of-assay-vllm.json").read_text())
    assert "Qwen/Qwen2.5-1.5B-Instruct" in json.dumps(doc)

def test_nosana_job_not_deployed_note():
    doc = json.loads((ROOT / "nosana/proof-of-assay-vllm.json").read_text())
    assert "NOT DEPLOYED" in doc["_notes"]

def test_article_is_draft():
    assert "DRAFT" in (ROOT / "ARTICLE.md").read_text()

def test_no_live_arweave_claim(results):
    assert "NOT_ANCHORED" in results["arweave"]
