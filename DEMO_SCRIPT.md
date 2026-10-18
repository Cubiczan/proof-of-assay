# Proof-of-Assay — Demo Script (~3 minutes)

> Synthetic-fixture audit demo plus the 2026-10-18 live run evidence. Say "synthetic" out loud for the lot data. The Nosana deployment ran live and was then stopped — do not present it as a currently running endpoint.

- **0:00 Problem.** Mine finance pays on assay + invoice pairs nobody can
  re-audit after the fact. AI that cannot be re-verified is a black box.
- **0:30 Run.** `python scripts/reproduce.py` — 8 synthetic lots, 5 clean,
  3 exceptions, **$289,849.19 cash at risk**. Show LOT-003 (grade),
  LOT-006 (quantity), LOT-007 (price).
- **1:20 Verify.** `python scripts/verify_chain.py` -> PASS (11 entries).
  Then `--tamper` -> FAIL. Open the Streamlit verifier, flip the tamper
  toggle, show FAIL live.
- **2:00 Live path (completed, then stopped).** Show `nosana/proof-of-assay-vllm.json`:
  Qwen2.5-1.5B-Instruct via vLLM (`vllm/vllm-openai:v0.10.2`) ran on Nosana
  2026-10-18 — deployment `9K9q9zJDhoybSoeY4eC7zMnmM7eaRPRp1CG5AHpPG6py`, job `CUB9FuZkdLH2Pr7jXBhwgovkSdseQwGXpNSSQcphaaEE`, RTX 3090 — and was stopped
  after the run. State plainly that the model's one live test answer was
  wrong and the deterministic rules flagged the exceptions. Receipt bundle
  anchored on Arweave: https://arweave.net/yTIbmFhgUS88RNaO2W92Oy7kPigpMyRUmToOeumLSus
- **2:45 Close.** Same documents + same rules + same chain head = same
  verdict, without trusting the operator. Repo + `results.json` are the evidence.
