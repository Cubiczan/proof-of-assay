"""Proof-of-Assay verifier (Streamlit).

Run: streamlit run streamlit_app.py
Shows the deterministic audit of the synthetic fixtures, the 11-entry
hash chain, and a tamper simulation: flipping one payload makes
verification FAIL. Links the 2026-10-18 live Nosana run (deployment
stopped after use) and the Arweave anchor of the verified receipt
bundle. The lot verdicts are produced by deterministic rules, not by
the live model — whose one live test answer was wrong (see ARTICLE.md).
"""
import copy
import streamlit as st
from proof_of_assay import run_audit, build_chain, verify_chain

st.set_page_config(page_title="Proof-of-Assay Verifier", layout="wide")
st.title("Proof-of-Assay — Verifiable Mining Audit")
st.warning("SYNTHETIC DATA — deterministic rules audit. Live Nosana run completed 2026-10-18 (deployment 9K9q9zJDhoybSoeY4eC7zMnmM7eaRPRp1CG5AHpPG6py, job CUB9FuZkdLH2Pr7jXBhwgovkSdseQwGXpNSSQcphaaEE, RTX 3090, now stopped); receipt anchored on Arweave (tx yTIbmFhgUS88RNaO2W92Oy7kPigpMyRUmToOeumLSus). The live 1.5B model's one test answer was wrong — the rules, not the model, flag the exceptions.")

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
if ok:
    st.success("Chain verification: PASS")
else:
    st.error("Chain verification: FAIL")

st.subheader("Tamper simulation")
if st.checkbox("Tamper with one receipt (demo)"):
    bad = copy.deepcopy(chain)
    bad[3]["payload"]["invoiced_amount_usd"] = 1.00
    if not verify_chain(bad):
        st.error("Chain verification: FAIL (tampered payload detected)")
    else:
        st.success("Chain verification: PASS")

st.caption("Live evidence (2026-10-18): Nosana deployment 9K9q9zJDhoybSoeY4eC7zMnmM7eaRPRp1CG5AHpPG6py / job CUB9FuZkdLH2Pr7jXBhwgovkSdseQwGXpNSSQcphaaEE served Qwen2.5-1.5B-Instruct via vLLM (vllm/vllm-openai:v0.10.2) on an RTX 3090 and was stopped after the run — it is not a running endpoint. Verified receipt bundle anchored on Arweave: https://arweave.net/yTIbmFhgUS88RNaO2W92Oy7kPigpMyRUmToOeumLSus · Repo: https://github.com/icohangar-ops/proof-of-assay")
