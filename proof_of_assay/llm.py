"""Optional OpenAI-compatible client for Nosana-hosted narration.

Lot verdicts are decided only by the deterministic rules in audit.py.
This module drafts a short explanation when NOSANA_LLM_BASE_URL is set
(typically a Nosana Ollama or vLLM endpoint). When the env is unset,
the endpoint is unreachable, or the request fails, callers get a skipped
result and the audit continues unchanged.

Environment:
  NOSANA_LLM_BASE_URL   e.g. https://<deployment>.node.k8s.prd.nos.ci
                        or https://host:11434  ( /v1 is appended if missing )
  NOSANA_LLM_API_KEY    optional; sent as Authorization: Bearer <key>
  NOSANA_LLM_MODEL      optional; default qwen2.5:7b
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from copy import deepcopy
from typing import Any, Optional

DEFAULT_MODEL = "qwen2.5:7b"
DEFAULT_TIMEOUT_SEC = 30
DEFAULT_MAX_TOKENS = 256

_SYSTEM = (
    "You explain mining-payables audit exceptions for a human reviewer. "
    "The lot verdict and cash-at-risk figures are already decided by "
    "deterministic rules; do not change or second-guess them. Write 2-4 "
    "plain sentences. Do not invent documents, grades, or amounts that "
    "are not in the JSON you are given."
)


def configured_base_url() -> Optional[str]:
    raw = (os.environ.get("NOSANA_LLM_BASE_URL") or "").strip()
    return raw or None


def configured_model() -> str:
    return (os.environ.get("NOSANA_LLM_MODEL") or DEFAULT_MODEL).strip() or DEFAULT_MODEL


def configured_api_key() -> Optional[str]:
    key = (os.environ.get("NOSANA_LLM_API_KEY") or "").strip()
    return key or None


def is_configured() -> bool:
    return configured_base_url() is not None


def _normalize_base(url: str) -> str:
    base = url.rstrip("/")
    if base.endswith("/v1"):
        return base
    if base.endswith("/v1/chat/completions"):
        return base[: -len("/chat/completions")]
    return base + "/v1"


def chat(
    messages: list[dict[str, str]],
    *,
    model: Optional[str] = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    timeout: float = DEFAULT_TIMEOUT_SEC,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Optional[str]:
    """POST /v1/chat/completions. Returns assistant text, or None on skip/error."""
    raw_base = base_url if base_url is not None else configured_base_url()
    if not raw_base:
        return None
    endpoint = _normalize_base(raw_base) + "/chat/completions"
    body = {
        "model": model or configured_model(),
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.2,
        "stream": False,
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    key = api_key if api_key is not None else configured_api_key()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError):
        return None
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return None
    if content is None:
        return None
    text = content if isinstance(content, str) else str(content)
    text = text.strip()
    return text or None


def explain_lot(decision: dict[str, Any], **chat_kwargs: Any) -> Optional[str]:
    """Narrate one already-decided lot. Returns None if unconfigured or on error."""
    if not (chat_kwargs.get("base_url") or configured_base_url()):
        return None
    user = (
        "Explain this audit decision. Do not change the status or amounts.\n\n"
        + json.dumps(decision, sort_keys=True, indent=2)
    )
    return chat(
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user},
        ],
        **chat_kwargs,
    )


def attach_narratives(results: dict[str, Any], **chat_kwargs: Any) -> dict[str, Any]:
    """Return a copy of results with optional `narrative` on each decision.

    The returned copy is for display only. Do not feed it to `build_chain`
    if you need the fixture chain head to stay stable — narratives are not
    part of the deterministic receipt.
    When the client is unconfigured, the copy is unchanged except for
    `narration` metadata describing the skip.
    """
    out = deepcopy(results)
    if not (chat_kwargs.get("base_url") or configured_base_url()):
        out["narration"] = {
            "status": "skipped",
            "reason": "NOSANA_LLM_BASE_URL is unset",
        }
        return out
    explained = 0
    failed = 0
    for decision in out.get("decisions") or []:
        text = explain_lot(decision, **chat_kwargs)
        if text:
            decision["narrative"] = text
            explained += 1
        else:
            failed += 1
    out["narration"] = {
        "status": "complete" if failed == 0 else "partial",
        "model": chat_kwargs.get("model") or configured_model(),
        "explained": explained,
        "failed": failed,
    }
    return out
