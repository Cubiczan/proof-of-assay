# Proof-of-Assay — Demo Script (~3 minutes)

> Fixture/local demo. Say "synthetic" and "planned" out loud where marked —
> do not claim a live Nosana job or Arweave tx that has not happened.

- **0:00 Problem.** Mine finance pays on assay + invoice pairs nobody can
  re-audit after the fact. AI that cannot be re-verified is a black box.
- **0:30 Run.** `python scripts/reproduce.py` — 8 synthetic lots, 5 clean,
  3 exceptions, **$289,849.19 cash at risk**. Show LOT-003 (grade),
  LOT-006 (quantity), LOT-007 (price).
- **1:20 Verify.** `python scripts/verify_chain.py` -> PASS (11 entries).
  Then `--tamper` -> FAIL. Open the Streamlit verifier, flip the tamper
  toggle, show FAIL live.
- **2:00 Planned live path.** Show `nosana/proof-of-assay-vllm.json`:
  Qwen2.5-1.5B-Instruct via vLLM on Nosana (Simple strategy, replica 1,
  short timeout). Receipts then anchor on Arweave (Turbo free tier, KB-sized).
  Explicitly: "not deployed yet — pending the hackathon credit claim."
- **2:45 Close.** Same documents + same rules + same chain head = same
  verdict, without trusting the operator. Repo + `results.json` are the evidence.
