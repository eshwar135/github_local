# gemini_wrapper.py
"""
REST-only wrapper for Google Generative Language API.
Reads GEMINI_API_KEY and GEMINI_MODEL at call-time (so callers can temporarily
override os.environ for a retry/fallback).
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()  # loads project .env, if present

# default base; can override with GEMINI_REST_BASE in .env
DEFAULT_BASE = "https://generativelanguage.googleapis.com/v1beta2"

def _extract_from_response_json(j):
    """Return the most likely text from Google Generative response shapes."""
    try:
        if isinstance(j, dict):
            if "candidates" in j and isinstance(j["candidates"], list) and j["candidates"]:
                c0 = j["candidates"][0]
                for k in ("content", "text", "output"):
                    if k in c0 and c0[k]:
                        return c0[k]
                return json.dumps(c0)
            for k in ("output", "response", "text"):
                if k in j and j[k]:
                    return j[k]
    except Exception:
        pass
    return json.dumps(j)

def call_gemini(prompt: str, max_output_tokens: int = 256, timeout: int = 60) -> str:
    """
    Call Google Generative REST API using the current environment variables.
    Returns generated text or an error string beginning with [gemini-...].
    """
    # Read API key & model at call time (allows temporary env changes)
    API_KEY = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")
    BASE = os.environ.get("GEMINI_REST_BASE", DEFAULT_BASE)

    if not API_KEY:
        return "[gemini-http-error] GEMINI_API_KEY not set."

    url = f"{BASE}/models/{MODEL}:generate?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    body = {
        "prompt": {"text": prompt},
        "maxOutputTokens": int(max_output_tokens)
    }

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=timeout)
    except Exception as e:
        return f"[gemini-http-error] Request failed: {e}"

    if resp.status_code != 200:
        # try to decode JSON body for better error message
        try:
            err = resp.json()
            return f"[gemini-http-error] status={resp.status_code} body={json.dumps(err)[:1000]}"
        except Exception:
            # empty body or non-json
            return f"[gemini-http-error] status={resp.status_code} text={resp.text[:1000]}"

    try:
        j = resp.json()
        return _extract_from_response_json(j)
    except Exception as e:
        return f"[gemini-http-error] bad-json: {e} body={resp.text[:1000]}"
