# Proof-of-Assay: Verifiable Mining Audit Agents on Decentralized GPU

> **DRAFT — DO NOT PUBLISH WITHOUT REVIEW.**
> Status: fixture/local build. Synthetic data only. No live Nosana
> deployment and no live Arweave anchor are claimed in this draft.
> Publish only on HackerNoon for the Decentralize AI hackathon
> (Round 1 deadline: Oct 31, 2026) after human review.

## Tags guidance (set on HackerNoon at publish time — do not publish yet)

- Required on every entry: `#decentralize-ai`, `#decentralize-ai-hackathon`
- Nosana (Killing The GPU Bottleneck): `#ai-inference`, `#gpu-cloud`, `#on-demand-gpus`, `#open-source-gpu-cloud`
- Arweave (Turning Black-Box AI Into Public Infrastructure): `#arweave`, `#permanent-storage`, `#decentralized-storage`
- HackerNoon open-AI theme: `#agentic-ai`, `#decentralized-ai`, `#depin`, `#open-source`, `#llms`

Use at least one sponsor tag set above plus the two required tags.

## Disclosure (keep in the published post)

> All mining documents in this post are **synthetic fixtures** created for
> this demo. Amounts are deterministic fixture arithmetic, not real mine
> payables. At draft time the system runs in **FIXTURE/LOCAL** mode: the
> Nosana deployment and Arweave anchoring described below are the planned
> live path, honestly badged as pending until they actually run.

## Context

Mine finance pays suppliers from assay certificates and invoices. When an
invoice grade, tonnage, or unit price drifts from the assay and contract,
the difference is cash paid for metal that was never delivered — and after
payment, nobody can re-run the decision. An AI auditor that cannot be
re-verified is just a faster black box.

Proof-of-Assay makes every audit decision reproducible: the same documents,
the same deterministic rules (and, in the live path, the same open-model
hash and prompt hash) must produce the same verdict, recorded in a
hash chain anyone can check without trusting the operator.

## Strategy

1. **Reconcile deterministically first.** Expected amount is
   `tonnes x contracted price`; grade, quantity, and amount variances flag
   exceptions and price the cash at risk. Rules — not the LLM — decide, so
   results reproduce without a GPU.
2. **Use the open model where it helps, not where it decides.** In the
   planned live path, Qwen2.5-1.5B-Instruct served by vLLM extracts and
   explains; its model ID/hash and prompt hash go into the receipt.
3. **Run inference on decentralized GPU.** The model is packaged as a
   Nosana job definition (`nosana/proof-of-assay-vllm.json` in the repo),
   to run with Simple strategy, one replica, and a short timeout so the
   $70 participant credit is spent in hours, not burned in days.
4. **Anchor receipts permanently.** Each run's receipt (document hashes,
   model hash, prompt hash, output, Nosana job ID) is a few KB — small
   enough for Arweave via the ar.io Turbo free tier, verified afterwards
   through a public gateway.
5. **Let anyone verify.** A Streamlit verifier shows the lots, the
   exceptions, the cash at risk, and the 11-entry hash chain — and demos
   tamper detection: change one payload and verification flips to FAIL.

## Model / Architecture

- **Audit core (live today, fixture mode):** Python, deterministic rules,
  SHA-256 hash chain (genesis + one entry per lot + summary + anchor slot).
- **Planned inference:** Qwen/Qwen2.5-1.5B-Instruct, vLLM OpenAI-compatible
  server, Nosana container job (GPU, port 8000) — see the repo job file.
- **Planned provenance:** Arweave receipt anchoring via Turbo (free tier
  for KB-sized receipts); gateway re-fetch + hash comparison to verify.
- **Verifier:** Streamlit app (`streamlit_app.py`) with an explicit
  FIXTURE/LOCAL badge and a tamper-simulation toggle.

## Evidence (fixture build)

- Public repo: https://github.com/icohangar-ops/proof-of-assay
- Reproduce: `python scripts/reproduce.py` → 8 synthetic lots, 5 clean,
  3 exceptions (grade / quantity / price), **$289,849.19 cash at risk**,
  11-entry hash chain — written to `results.json`.
- Verify: `python scripts/verify_chain.py` → PASS; `--tamper` → FAIL.
- Tests: 35 pytest tests covering the headline numbers, each exception
  type, chain integrity, tamper detection, and the honesty badges
  (fixture mode, not-deployed Nosana file, draft article).

## Limitations (honest)

- Synthetic fixtures only; no real assay or invoice has been processed.
- Nosana inference and Arweave anchoring are **not live yet** — they are
  pending the hackathon credit claim and approvals, and this post will be
  updated (plus a Nosana follow-up post) only when there is a real job ID
  and a real Arweave transaction to link.

## What happens next

Claim the $70 Nosana participant credit with this repo, deploy the vLLM
job in a short stopped-after-use session, anchor the first real receipt,
and publish the follow-up showing the job ID, the credit spend, and the
gateway-verified Arweave record.
