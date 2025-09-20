import json
import time
import pytest
from unittest.mock import patch

# import the Flask app and adapter object
from app import app as flask_app  # app is the Flask instance
from app import adapter

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client

def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    j = resp.get_json()
    assert j.get("ok") is True
    assert "adapter" in j

def test_generate_success(client, monkeypatch):
    # keep the existing pattern: monkeypatch adapter.generate to avoid network calls
    def fake_generate(prompt, max_tokens=256, temperature=0.0):
        return f"FAKE-RESPONSE for: {prompt[:20]}"
    monkeypatch.setattr(adapter, "generate", fake_generate)

    payload = {"prompt": "Hello world"}
    rv = client.post("/api/generate", data=json.dumps(payload), content_type="application/json")
    assert rv.status_code == 200
    j = rv.get_json()
    assert "output" in j
    assert "FAKE-RESPONSE" in j["output"]

def test_generate_missing_prompt(client):
    rv = client.post("/api/generate", data=json.dumps({}), content_type="application/json")
    # app returns 400 for missing prompt
    assert rv.status_code == 400
    j = rv.get_json()
    assert j.get("error") in ("prompt required", "invalid_input")

def test_clamping_tokens_and_temperature(client, monkeypatch):
    """
    Ensure the app clamps max_tokens to <= MAX_ALLOWED_TOKENS and temperature to <= 1.0.
    We monkeypatch adapter.generate to capture values the app passes to it.
    """
    captured = {}

    def capturing_generate(prompt, max_tokens=256, temperature=0.0):
        captured["prompt"] = prompt
        captured["max_tokens"] = max_tokens
        captured["temperature"] = temperature
        return "OK"

    monkeypatch.setattr(adapter, "generate", capturing_generate)

    # Use extreme values that should be clamped by the prompt_service
    payload = {"prompt": "Clamp check", "max_output_tokens": 999999, "temperature": 5.0}
    rv = client.post("/api/generate", data=json.dumps(payload), content_type="application/json")
    assert rv.status_code == 200
    assert captured.get("prompt") == "Clamp check"
    # max_tokens must be an int and <= 1024 (MAX_ALLOWED_TOKENS in prompt_service)
    assert isinstance(captured.get("max_tokens"), int)
    assert captured.get("max_tokens") <= 1024
    # temperature must be clamped to <= 1.0
    assert captured.get("temperature") <= 1.0

def test_rate_limit(client, monkeypatch):
    """
    Temporarily lower RATE_LIMIT_MAX and RATE_LIMIT_WINDOW to make the test fast,
    then issue requests until we get a 429.
    """
    # import module-level rate limit variables from app
    import app as app_module

    # save original values and restore after test
    orig_window = app_module.RATE_LIMIT_WINDOW
    orig_max = app_module.RATE_LIMIT_MAX
    try:
        app_module.RATE_LIMIT_WINDOW = 2  # 2-second window
        app_module.RATE_LIMIT_MAX = 3     # allow only 3 requests

        # clear any existing timestamps so test starts with a clean slate
        app_module.RATE_LIMIT.clear()

        # monkeypatch adapter.generate to be fast and deterministic
        monkeypatch.setattr(adapter, "generate", lambda prompt, max_tokens=256, temperature=0.0: "OK")

        # Make allowed requests
        for i in range(app_module.RATE_LIMIT_MAX):
            rv = client.post("/api/generate", data=json.dumps({"prompt": f"req {i}"}), content_type="application/json")
            assert rv.status_code == 200

        # Next request should be rate-limited (429)
        rv = client.post("/api/generate", data=json.dumps({"prompt": "should rate limit"}), content_type="application/json")
        assert rv.status_code == 429
        j = rv.get_json()
        assert j.get("error") == "rate_limited"

    finally:
        # restore originals
        app_module.RATE_LIMIT_WINDOW = orig_window
        app_module.RATE_LIMIT_MAX = orig_max
        # clear RATE_LIMIT store to avoid polluting other tests
        app_module.RATE_LIMIT.clear()
