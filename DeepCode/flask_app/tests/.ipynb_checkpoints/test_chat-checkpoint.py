import json
import pytest
from unittest.mock import patch

from app import app as flask_app
from app import adapter
import services.chat_service as cs

@pytest.fixture
def client():
    with flask_app.test_client() as client:
        yield client

def test_chat_start_and_message_flow(client, monkeypatch):
    # monkeypatch adapter.generate to return an echo-like reply
    def fake_generate(prompt, max_tokens=256, temperature=0.0):
        # return a reply that includes part of prompt so we verify storage
        return f"assistant reply to: {prompt[:30]}"

    monkeypatch.setattr(adapter, "generate", fake_generate)

    # start new session
    rv = client.post("/api/chat/start", data=json.dumps({}), content_type="application/json")
    assert rv.status_code == 200
    j = rv.get_json()
    assert j.get("ok") is True
    sid = j.get("session_id")
    assert sid

    # send a user message
    rv2 = client.post("/api/chat/message", data=json.dumps({"session_id": sid, "message": "Hello chat"}), content_type="application/json")
    assert rv2.status_code == 200
    j2 = rv2.get_json()
    assert j2.get("ok") is True
    assert "reply" in j2

    # fetch history
    rv3 = client.get(f"/api/chat/history/{sid}")
    assert rv3.status_code == 200
    j3 = rv3.get_json()
    assert j3.get("ok") is True
    hist = j3.get("history")
    # history should contain user and assistant messages
    roles = [m.get("role") for m in hist]
    assert "user" in roles
    assert "assistant" in roles

def test_chat_missing_fields(client):
    # missing session_id / message
    rv = client.post("/api/chat/message", data=json.dumps({}), content_type="application/json")
    assert rv.status_code == 400
