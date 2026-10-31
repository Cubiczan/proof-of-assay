# proof-of-assay — context

## Purpose

An audit agent pattern for mining payables: assay certificates and supplier invoices are reconciled lot by lot, exceptions are priced as cash at risk, and every decision is written into a SHA-256 hash chain that anyone can re-verify. On 2026-10-18 the open-weight model (Qwen2.5-1.5B-Instruct via vLLM, pinned image `vllm/vllm-openai:v0.10.2`) was served live on a Nosana RTX 3090 deployment and stopped after the run, and the verified receipt bundle was anchored on Arweave via the Turbo free tier. The audit + verification layer remains fully reproducible locally without a GPU.

## Architecture

Stack: Python.

Top-level layout:

- `data/`
- `nosana/`
- `proof_of_assay/`
- `scripts/`
- `tests/`
- `ARTICLE.md`
- `DEMO_SCRIPT.md`
- `README.md`
- `cover.png`
- `coverage.xml`
- `live_evidence.json`
- `requirements.txt`
- `results.json`
- `streamlit_app.py`

## How to run

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/reproduce.py     # writes results.json
python scripts/verify_chain.py  # PASS
python scripts/verify_chain.py --tamper  # FAIL (tamper demo)
pytest -q                       # 35 tests
streamlit run streamlit_app.py  # verifier UI
```

## Tests

```bash
python -m pytest -q
```

Coverage report: `coverage.xml` (generated 2026-10-31).

## Data note

Synthetic data only. Fixtures, samples and docs use fictional names and companies, example.com / .example emails, 555 phone numbers and placeholder keys (REPLACE_ME or env-var references). Statutes, regulations and public filings are cited as public record. No customer data is included.

See README.md for full details.
