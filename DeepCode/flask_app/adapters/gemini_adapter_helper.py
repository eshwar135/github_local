import logging
from typing import Optional

logger = logging.getLogger(__name__)

def _extract_text_from_response(resp) -> Optional[str]:
    """
    Try common patterns to extract generated text from a response object.
    """
    try:
        # common pattern: resp.candidates[0].content / output
        if hasattr(resp, "candidates") and resp.candidates:
            cand = resp.candidates[0]
            for field in ("content", "output", "text", "result"):
                if hasattr(cand, field):
                    val = getattr(cand, field)
                    if isinstance(val, (list, tuple)) and val:
                        # try to pull first text-like block
                        for block in val:
                            if isinstance(block, dict) and "text" in block:
                                return block["text"]
                            if hasattr(block, "text"):
                                return getattr(block, "text")
                        return str(val)
                    return str(val)
            return str(cand)

        # direct attributes on resp
        for attr in ("text", "result", "output", "response"):
            if hasattr(resp, attr):
                return str(getattr(resp, attr))

        # fallback to __dict__ values
        d = getattr(resp, "__dict__", None)
        if d:
            for v in d.values():
                if isinstance(v, str) and v.strip():
                    return v
    except Exception:
        logger.exception("extract_text error")
    return None

def generate_from_model(model, prompt: str, max_output_tokens: int = 256) -> dict:
    """
    Try several generation entrypoints and return a dict with debug info:
      { "ok": bool, "text": str|None, "debug": {...}, "error": optional }
    """
    debug = {"tried": []}
    try:
        # 1) generate_content (preferred)
        if hasattr(model, "generate_content"):
            debug["tried"].append("generate_content")
            try:
                resp = model.generate_content([{"type": "text_input", "text": prompt}], max_output_tokens=max_output_tokens)
                text = _extract_text_from_response(resp)
                return {"ok": True, "text": text, "debug": debug}
            except Exception as e:
                debug["generate_content_error"] = repr(e)

        # 2) start_chat (chat-style)
        if hasattr(model, "start_chat"):
            debug["tried"].append("start_chat")
            try:
                chat = model.start_chat()
                if hasattr(chat, "add_user_message"):
                    chat.add_user_message(prompt)
                elif hasattr(chat, "user_message"):
                    chat.user_message(prompt)
                if hasattr(chat, "respond_once"):
                    resp = chat.respond_once()
                elif hasattr(chat, "get_response"):
                    resp = chat.get_response()
                else:
                    resp = chat
                text = _extract_text_from_response(resp)
                return {"ok": True, "text": text, "debug": debug}
            except Exception as e:
                debug["start_chat_error"] = repr(e)

        # 3) generic fallbacks (other method names)
        for name in ("generate", "create", "generate_text"):
            if hasattr(model, name):
                debug["tried"].append(name)
                try:
                    fn = getattr(model, name)
                    resp = fn(prompt)
                    text = _extract_text_from_response(resp)
                    return {"ok": True, "text": text, "debug": debug}
                except Exception as e:
                    debug[f"{name}_error"] = repr(e)

        return {"ok": False, "text": None, "debug": debug, "error": "no-generation-entrypoint-found"}
    except Exception as e:
        logger.exception("unexpected adapter error")
        return {"ok": False, "text": None, "debug": debug, "error": repr(e)}
