# Proof-of-Assay: Verifiable Mining Audit Agents on Decentralized GPU

> **Synthetic-data disclosure:** All mining documents in this post are
> **synthetic fixtures** created for this demo. Amounts are deterministic
> fixture arithmetic, not real mine payables. No real assay or invoice
> has been processed.

> Status: ready for human review — not yet published. Live Nosana and
> Arweave evidence from 18 October 2026 is included below with real
> deployment, job, and transaction IDs. The Nosana deployment was
> stopped after the run; it is not a continuously running service.

## Tags (set on HackerNoon at publish time)

- Required on every entry: `#decentralize-ai`, `#decentralize-ai-hackathon`
- Nosana (Killing The GPU Bottleneck): `#ai-inference`, `#gpu-cloud`, `#on-demand-gpus`, `#open-source-gpu-cloud`
- Arweave (Turning Black-Box AI Into Public Infrastructure): `#arweave`, `#permanent-storage`, `#decentralized-storage`
- HackerNoon open-AI theme: `#agentic-ai`, `#decentralized-ai`, `#depin`, `#open-source`, `#llms`

Use at least one sponsor tag set above plus the two required tags.

## Context

Mine finance pays suppliers from assay certificates and invoices. When an
invoice grade, tonnage, or unit price drifts from the assay and contract,
the difference is cash paid for metal that was never delivered — and after
payment, nobody can re-run the decision. An AI auditor that cannot be
re-verified is just a faster black box.

Proof-of-Assay makes every audit decision reproducible: the same documents
and the same deterministic rules must produce the same verdict, recorded
in a hash chain anyone can check without trusting the operator.

## Strategy

1. **Reconcile deterministically first.** Expected amount is
   `tonnes x contracted price`; grade, quantity, and amount variances flag
   exceptions and price the cash at risk. Rules — not the LLM — decide, so
   results reproduce without a GPU.
2. **Use the open model where it helps, not where it decides.**
   Qwen2.5-1.5B-Instruct served by vLLM is the narration/extraction layer.
   It does not decide the lot verdicts (see the live test below, where
   the raw model got the answer wrong).
3. **Run inference on decentralized GPU.** The model was served from a
   Nosana deployment using the pinned image
   `vllm/vllm-openai:v0.10.2` (see Live run evidence), with a short
   stopped-after-use session so participant credit is spent in minutes,
   not burned in days.
4. **Anchor receipts permanently.** The verified receipt bundle (the full
   11-entry hash chain plus the audit summary and live-run evidence) was
   anchored on Arweave via the ar.io Turbo free tier and can be re-fetched
   from a public gateway (see Live run evidence).
5. **Let anyone verify.** A Streamlit verifier shows the lots, the
   exceptions, the cash at risk, and the 11-entry hash chain — and demos
   tamper detection: change one payload and verification flips to FAIL.

## Model / Architecture

- **Audit core:** Python, deterministic rules, SHA-256 hash chain
  (genesis + one entry per lot + summary + anchor-placeholder slot).
- **Live inference (run completed, then stopped):**
  Qwen/Qwen2.5-1.5B-Instruct, vLLM OpenAI-compatible server
  (`vllm/vllm-openai:v0.10.2`, max model length 4096, port 8000) on a
  Nosana NVIDIA RTX 3090 deployment — see `nosana/proof-of-assay-vllm.json`.
- **Provenance:** Arweave receipt anchoring via Turbo free tier;
  gateway re-fetch + SHA-256 comparison to verify.
- **Verifier:** Streamlit app (`streamlit_app.py`) showing the synthetic
  fixture audit, the chain, and a tamper-simulation toggle. It links the
  live Nosana IDs and the Arweave anchor below; the deployment itself is
  stopped and is not claimed to be running.

## Evidence (fixture audit)

- Public repo: https://github.com/icohangar-ops/proof-of-assay
- Live verifier: https://icohangar-lot-verifier.streamlit.app/
- Reproduce: `python scripts/reproduce.py` → 8 synthetic lots, 5 clean,
  3 exceptions (grade / quantity / price), **$289,849.19 cash at risk**,
  11-entry hash chain — written to `results.json`.
- Verify: `python scripts/verify_chain.py` → PASS; `--tamper` → FAIL.
- Machine-readable live evidence: `live_evidence.json` in the repo.

## Live run evidence (18 October 2026)

### Nosana — live, then stopped

- Serving deployment: `9K9q9zJDhoybSoeY4eC7zMnmM7eaRPRp1CG5AHpPG6py`
- Serving job: `CUB9FuZkdLH2Pr7jXBhwgovkSdseQwGXpNSSQcphaaEE`
- GPU / price: NVIDIA RTX 3090 24GB at $0.19/h
  (market `CA5pMpqkYFKtme7K31pNB1s62X2SdhEv1nN9RdxKCpuQ`)
- Image / model: `vllm/vllm-openai:v0.10.2` serving
  `Qwen/Qwen2.5-1.5B-Instruct`, max model length 4096
- Endpoint check: `GET /v1/models` returned HTTP 200 at 22:00:55 UTC,
  about 2 minutes after the deployment was created.
- Stop transaction (serving deployment):
  `8ayoF3Rar1VgJ3dxFsLv6jgEeW33rhX9bxryEWvTJexTRNPZ3T8QAXFG6Z8mpJA2DVLyVdbzxF9ymv3MLxjgoy7`
- Cost: total spend across both deployments was about $0.26, leaving
  about $69.70 of the $70 participant credit.
- What did not go smoothly, stated plainly: a first deployment
  (`EoxQqgJqLABH9A5bZpUxzmJZN6gPHhzwDmGUJpmQLkZn`) stalled pulling the
  `:latest` vLLM image and was stopped (stop transaction
  `3nK38ApeiLXG4h8Fv1EvE275G5fXAQmKrRBU6uVB7uDuroz8jJUNBJSEHLWCEdVcPtaTLyLE4QpgdeiZy2BcX5Tt`);
  pinning `v0.10.2` fixed that. The first serving job
  (`7Xkyj1TmuzaoG7Gaoek3YshDgRpp8Q1oaDLVZKxfxsL8`) crashed and Nosana
  auto-replaced it with the serving job above.

### The live model test — the raw model was wrong

The served model was asked, in effect, to say EXCEPTION or CLEAN for a
lot assaying 2.41 g/t Au against 3.10 g/t expected. It replied exactly:

> CLEAN - The assay result falls within the expected range of 3.10 g/t.

That answer is **wrong**: 2.41 g/t is about 22% below 3.10 g/t and should
be flagged EXCEPTION. This is why Proof-of-Assay does not trust the raw
1.5B model to audit alone. The 1.5B open model is the
narration/extraction layer; the deterministic tolerance rules and the
hash chain are what actually flagged the 3 exceptions and priced the
$289,849.19 cash at risk in the 8-lot audit. The live run proves the
decentralized serving path works; it does not prove — and this post does
not claim — that a 1.5B model reliably audits by itself.

### Arweave — receipt anchored

- Transaction ID: `yTIbmFhgUS88RNaO2W92Oy7kPigpMyRUmToOeumLSus`
- Gateway: https://arweave.net/yTIbmFhgUS88RNaO2W92Oy7kPigpMyRUmToOeumLSus
- Turbo gateway (same payload): https://turbo-gateway.com/raw/yTIbmFhgUS88RNaO2W92Oy7kPigpMyRUmToOeumLSus
- Payload: 12,473 bytes (the verified receipt bundle: 8-lot audit,
  11-entry hash chain with head
  `907c7041a4a27a44941acf90699a019c8cfe08b0eb4d3f7ef9c3636c8c6cd5ac`,
  verification PASS, plus the Nosana evidence above)
- Payload SHA-256:
  `14f0cc328daa1c82d9d85ef5f337afd8d693e3c53ef084e3a84358ab8b2432fc`
- Turbo cost: winc 0 (free tier; remainder of the wallet's free
  allowance was 10 MiB before upload). No credits were bought, by card
  or crypto, and the local signer wallet was never funded.
- Note on the chain format: entry 10 of the anchored chain is the
  historical anchor-placeholder slot. The live transaction ID is
  recorded here and in `live_evidence.json`, outside the chain, because
  embedding the transaction ID inside the chain payload would change
  the chain head that the transaction anchors.

## Limitations (honest)

- Synthetic fixtures only; no real assay or invoice has been processed.
- The Nosana deployment was a short live run and is now **stopped**;
  there is no continuously running inference endpoint to query.
- The raw 1.5B model's one live test answer was wrong (above). The audit
  verdicts come from deterministic rules, not from the model.
- One test completion was run live; no claim is made about model
  accuracy beyond that single, incorrect, result.

## What happens next

Publish this post on HackerNoon with the tags above, publish the Nosana
follow-up showing how the credits were used, and — in a longer session —
test whether a larger open model handles the narration/extraction layer
more reliably, while keeping the deterministic rules as the decider.
