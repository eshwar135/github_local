# services/chat_service.py
import uuid
import time
from typing import Dict, List, Any, Optional

# Simple in-memory session store for conversation state.
# Structure: sessions[session_id] = {"created": ts, "last_active": ts, "messages": [ {"role": "user"/"assistant", "text": "..."} ]}
sessions: Dict[str, Dict[str, Any]] = {}

# Configurable session behavior
SESSION_TTL_SECONDS = 60 * 60 * 24  # 24 hours lifetime
MAX_HISTORY_MESSAGES = 50  # keep last N messages per session

class ChatError(RuntimeError):
    pass

def _now() -> float:
    return time.time()

def create_session(initial_user_message: Optional[str] = None) -> str:
    session_id = str(uuid.uuid4())
    ts = _now()
    sessions[session_id] = {
        "created": ts,
        "last_active": ts,
        "messages": []
    }
    if initial_user_message:
        push_user_message(session_id, initial_user_message)
    return session_id

def _prune_session_history(session_id: str):
    s = sessions.get(session_id)
    if not s:
        return
    msgs = s["messages"]
    if len(msgs) > MAX_HISTORY_MESSAGES:
        # preserve latest messages
        sessions[session_id]["messages"] = msgs[-MAX_HISTORY_MESSAGES:]

def push_user_message(session_id: str, text: str):
    if session_id not in sessions:
        raise ChatError("session_not_found")
    sessions[session_id]["messages"].append({"role": "user", "text": text})
    sessions[session_id]["last_active"] = _now()
    _prune_session_history(session_id)

def push_assistant_message(session_id: str, text: str):
    if session_id not in sessions:
        raise ChatError("session_not_found")
    sessions[session_id]["messages"].append({"role": "assistant", "text": text})
    sessions[session_id]["last_active"] = _now()
    _prune_session_history(session_id)

def get_history(session_id: str) -> List[Dict[str, str]]:
    s = sessions.get(session_id)
    if not s:
        raise ChatError("session_not_found")
    return list(s["messages"])

def cleanup_expired_sessions():
    now = _now()
    expired = [sid for sid, s in sessions.items() if (s["last_active"] + SESSION_TTL_SECONDS) < now]
    for sid in expired:
        del sessions[sid]

def session_exists(session_id: str) -> bool:
    return session_id in sessions
