# chat.py
from flask import Blueprint, request, jsonify, current_app
from services.chat_service import (
    create_session, push_user_message, push_assistant_message,
    get_history, cleanup_expired_sessions, session_exists, ChatError
)
import google.generativeai as ggen
import os

bp = Blueprint("chat", __name__)

# helper to produce assistant response using the adapter (ggen)
def _call_assistant_via_adapter(prompt: str, max_tokens: int = 256, temperature: float = 0.0) -> str:
    """
    Use the same model flow as app: get model object and call adapter-compatible generation.
    This expects google.generativeai configured (ggen.configure done at app startup).
    """
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    model = None
    # prefer GenerativeModel API if available
    if hasattr(ggen, "GenerativeModel"):
        try:
            gm = ggen.GenerativeModel(model_name)
            # Many versions accept a single prompt string
            resp = gm.generate_content(prompt)
            # Attempt to return .text if present
            if hasattr(resp, "text") and resp.text:
                return resp.text
            # fallback to candidates
            if hasattr(resp, "candidates") and resp.candidates:
                return str(resp.candidates[0])
            return str(resp)
        except Exception:
            # fallback to get_model
            pass

    if hasattr(ggen, "get_model"):
        model = ggen.get_model(model_name)
        # try basic generate_content with prompt
        if hasattr(model, "generate_content"):
            resp = model.generate_content(prompt)
            if hasattr(resp, "text") and resp.text:
                return resp.text
            if hasattr(resp, "candidates") and resp.candidates:
                return str(resp.candidates[0])
            return str(resp)

    # if we reach here, raise to be handled by caller
    raise RuntimeError("no_generation_entrypoint")

@bp.post("/chat/start")
def chat_start():
    """
    Start a new chat session. Optional JSON: {"prompt": "initial message"}
    Returns: {"ok": True, "session_id": "..."}
    """
    cleanup_expired_sessions()
    data = request.get_json(silent=True) or {}
    initial = data.get("prompt")
    sid = create_session(initial_user_message=initial) if initial else create_session()
    return jsonify({"ok": True, "session_id": sid})

@bp.post("/chat/message")
def chat_message():
    """
    Send a user message to an existing session and get assistant reply.
    JSON: {"session_id": "<id>", "message": "<text>", "max_output_tokens": optional, "temperature": optional}
    Returns: {"ok": True, "reply": "...", "session_id": "..."}
    """
    cleanup_expired_sessions()
    data = request.get_json(silent=True) or {}
    session_id = data.get("session_id")
    message = data.get("message") or data.get("prompt")
    if not session_id or not message:
        return jsonify({"error": "session_id and message required"}), 400
    if not session_exists(session_id):
        return jsonify({"error": "session_not_found"}), 404

    # push user message to history
    try:
        push_user_message(session_id, message)
    except ChatError:
        return jsonify({"error": "session_not_found"}), 404

    # Compose a short context string for the assistant: join last few messages
    history = get_history(session_id)
    context_parts = []
    for m in history[-10:]:
        role = m["role"]
        text = m["text"]
        context_parts.append(f"{role}: {text}")
    # include the new user message at the end
    context_parts.append(f"user: {message}")
    prompt_for_model = "\n".join(context_parts)

    # call the underlying model via ggen-compatible flow
    try:
        reply = _call_assistant_via_adapter(prompt_for_model)
    except Exception as e:
        # return an error but keep session state
        current_app.logger.exception("Assistant generation failed")
        return jsonify({"error": "generation_failed", "detail": str(e)}), 500

    # store assistant reply and return
    try:
        push_assistant_message(session_id, reply)
    except ChatError:
        return jsonify({"error": "session_not_found"}), 404

    return jsonify({"ok": True, "reply": reply, "session_id": session_id})

@bp.get("/chat/history/<session_id>")
def chat_history(session_id):
    cleanup_expired_sessions()
    try:
        hist = get_history(session_id)
        return jsonify({"ok": True, "session_id": session_id, "history": hist})
    except ChatError:
        return jsonify({"error": "session_not_found"}), 404
