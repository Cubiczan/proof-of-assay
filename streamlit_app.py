"""Proof-of-Assay verifier (Streamlit). FIXTURE/LOCAL mode.

Run: streamlit run streamlit_app.py
Shows the deterministic audit, the 11-entry hash chain, and a tamper
simulation: flipping one payload makes verification FAIL.
"""
import copy
import streamlit as st
from proof_of_assay import run_audit, build_chain, verify_chain

st.set_page_config(page_title="Proof-of-Assay Verifier", layout="wide")
st.title("Proof-of-Assay — Verifiable Mining Audit")
st.warning("FIXTURE / LOCAL — synthetic data, deterministic rules. No live Nosana deployment and no live Arweave anchor are claimed yet.")

results = run_audit()
chain = build_chain(results)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Lots", results["total_lots"])
c2.metric("Clean", results["clean_count"])
c3.metric("Exceptions", results["exception_count"])
c4.metric("Cash at risk (USD)", f"${results['cash_at_risk_usd']:,.2f}")

st.subheader("Lot decisions")
st.dataframe(results["decisions"], use_container_width=True)

st.subheader("Hash chain")
st.write(f"Entries: {len(chain)} · Head: `{chain[-1]['hash']}`")
st.code("\n".join(f"{e['index']:>2} {e['type']:<18} {e['hash'][:16]}..." for e in chain))

ok = verify_chain(chain)
st.success("Chain verification: PASS") if ok else st.error("Chain verification: FAIL")

st.subheader("Tamper simulation")
if st.checkbox("Tamper with one receipt (demo)"):
    bad = copy.deepcopy(chain)
    bad[3]["payload"]["invoiced_amount_usd"] = 1.00
    st.error("Chain verification: FAIL (tampered payload detected)") if not verify_chain(bad) else st.success("Chain verification: PASS")

st.caption("Planned live path: Qwen2.5-1.5B-Instruct via vLLM on Nosana (nosana/proof-of-assay-vllm.json); receipts anchored on Arweave via Turbo free tier. Neither is claimed live in this fixture build.")
