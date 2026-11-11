import json
from pathlib import Path
from unittest.mock import patch
import urllib.error

import pytest

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT))
from proof_of_assay import attach_narratives, build_chain, chat, explain_lot, is_configured, run_audit, verify_chain
from proof_of_assay import llm as llm_mod


@pytest.fixture
def clean_env(monkeypatch):
    monkeypatch.delenv("NOSANA_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("NOSANA_LLM_API_KEY", raising=False)
    monkeypatch.delenv("NOSANA_LLM_MODEL", raising=False)


def test_is_configured_false_when_unset(clean_env):
    assert is_configured() is False


def test_chat_returns_none_when_unset(clean_env):
    assert chat([{"role": "user", "content": "hi"}]) is None


def test_explain_lot_returns_none_when_unset(clean_env):
    results = run_audit()
    assert explain_lot(results["decisions"][0]) is None


def test_attach_narratives_skips_without_mutating_chain(clean_env):
    results = run_audit()
    chain = build_chain(results)
    narrated = attach_narratives(results)
    assert narrated["narration"]["status"] == "skipped"
    assert all("narrative" not in d for d in narrated["decisions"])
    assert build_chain(results) == chain
    assert verify_chain(chain) is True


def test_attach_narratives_does_not_change_fixture_verdicts(clean_env):
    results = run_audit()
    narrated = attach_narratives(results)
    assert narrated["cash_at_risk_usd"] == results["cash_at_risk_usd"] == 289849.19
    assert [d["status"] for d in narrated["decisions"]] == [d["status"] for d in results["decisions"]]


class _FakeResp:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode()
    def read(self):
        return self._payload
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False


def test_chat_posts_openai_compatible_body(clean_env, monkeypatch):
    monkeypatch.setenv("NOSANA_LLM_BASE_URL", "https://example.invalid")
    monkeypatch.setenv("NOSANA_LLM_API_KEY", "test-key-not-real")
    monkeypatch.setenv("NOSANA_LLM_MODEL", "qwen2.5:7b")
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        captured["headers"] = {k.lower(): v for k, v in {**getattr(req, 'unredirected_hdrs', {}), **req.headers}.items()}
        captured["body"] = json.loads(req.data.decode())
        captured["timeout"] = timeout
        return _FakeResp({
            "choices": [{"message": {"role": "assistant", "content": "  Grade drifted below the assay.  "}}]
        })

    monkeypatch.setattr(llm_mod.urllib.request, "urlopen", fake_urlopen)
    text = chat([{"role": "user", "content": "explain"}])
    assert text == "Grade drifted below the assay."
    assert captured["url"] == "https://example.invalid/v1/chat/completions"
    assert captured["body"]["model"] == "qwen2.5:7b"
    assert captured["body"]["stream"] is False
    assert captured["body"]["messages"][0]["content"] == "explain"
    assert captured["headers"].get("authorization") == "Bearer test-key-not-real"
    assert captured["timeout"] == llm_mod.DEFAULT_TIMEOUT_SEC


def test_normalize_keeps_existing_v1(clean_env, monkeypatch):
    monkeypatch.setenv("NOSANA_LLM_BASE_URL", "https://host.example/v1")
    captured = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.full_url
        return _FakeResp({"choices": [{"message": {"content": "ok"}}]})

    monkeypatch.setattr(llm_mod.urllib.request, "urlopen", fake_urlopen)
    assert chat([{"role": "user", "content": "x"}]) == "ok"
    assert captured["url"] == "https://host.example/v1/chat/completions"


def test_chat_returns_none_on_http_error(clean_env, monkeypatch):
    monkeypatch.setenv("NOSANA_LLM_BASE_URL", "https://example.invalid")

    def fake_urlopen(req, timeout=None):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(llm_mod.urllib.request, "urlopen", fake_urlopen)
    assert chat([{"role": "user", "content": "x"}]) is None


def test_attach_narratives_adds_text_when_endpoint_works(clean_env, monkeypatch):
    monkeypatch.setenv("NOSANA_LLM_BASE_URL", "https://example.invalid")

    def fake_urlopen(req, timeout=None):
        return _FakeResp({"choices": [{"message": {"content": "Rules flagged a grade mismatch."}}]})

    monkeypatch.setattr(llm_mod.urllib.request, "urlopen", fake_urlopen)
    results = run_audit()
    original_head = build_chain(results)[-1]["hash"]
    narrated = attach_narratives(results)
    assert narrated["narration"]["status"] == "complete"
    assert narrated["narration"]["explained"] == 8
    assert all(d["narrative"] == "Rules flagged a grade mismatch." for d in narrated["decisions"])
    # chain built from the original results is unchanged
    assert build_chain(results)[-1]["hash"] == original_head


def test_new_job_definition_is_ollama_qwen25_7b():
    doc = json.loads((ROOT / "nosana/proof-of-assay-llm.json").read_text())
    dumped = json.dumps(doc)
    assert doc["version"] == "0.1"
    assert doc["ops"][0]["args"]["image"] == "docker.io/ollama/ollama:0.32.6"
    assert doc["global"]["variables"]["MODEL"] == "qwen2.5:7b"
    assert "qwen2.5:7b" in dumped
    assert doc["ops"][0]["args"]["gpu"] is True
    ports = doc["ops"][0]["args"]["expose"]
    assert any(p.get("port") == 11434 for p in ports)
    assert "NOSANA_LLM" not in dumped
    assert "nos_" not in dumped.lower()
