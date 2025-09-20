# gemini_client.py
"""
Robust adapter for various Google Gemini SDK variants found on different installs.
It tries multiple client libraries and multiple method signatures until one works.

Place your GEMINI_API_KEY or GEMINI_API_KEY_FILE in the flask_app/.env or
set environment variables before starting Flask.

Typical usage:
    from gemini_client import generate_text
    generate_text("hello")
"""
import os, json, traceback
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# Read key (either raw key or a key-file path)
api_key = os.getenv("GEMINI_API_KEY")
api_key_file = os.getenv("GEMINI_API_KEY_FILE")
if not api_key and api_key_file and os.path.exists(api_key_file):
    with open(api_key_file, "r", encoding="utf-8") as f:
        api_key = f.read().strip()

# If still no api_key, don't crash at import — raise at call time with informative message.
MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

def _ensure_key():
    if not api_key:
        raise RuntimeError(
            "Gemini API key not found. Set GEMINI_API_KEY in flask_app/.env or point GEMINI_API_KEY_FILE to a file containing the key."
        )

def _try_call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        # return a tuple to indicate failure + exception for debugging
        return ("__CALL_FAIL__", e, traceback.format_exc())

def _use_google_generativeai(prompt, max_output_tokens=256):
    """
    Uses google.generativeai (google-generativeai package) where model objects expose generate_content/generate_content_async.
    """
    try:
        import google.generativeai as ggen
    except Exception as e:
        return ("__NO_SDK__", f"google.generativeai import failed: {e}")

    # configure (if available)
    try:
        if hasattr(ggen, "configure"):
            # prefer direct configure
            ggen.configure(api_key=api_key)
        else:
            # fallback: set environment variable the SDK may read
            os.environ["GOOGLE_API_KEY"] = api_key
    except Exception as e:
        # proceed — the next calls may still fail
        pass

    # 1) try ggen.get_model(MODEL)
    try:
        if hasattr(ggen, "get_model"):
            model = ggen.get_model(MODEL)
            # model may have generate_content
            if hasattr(model, "generate_content"):
                # try different argument names
                for kwargs in (
                    {"input": prompt, "max_output_tokens": max_output_tokens},
                    {"prompt": prompt, "max_output_tokens": max_output_tokens},
                    {"text": prompt, "max_output_tokens": max_output_tokens},
                ):
                    res = _try_call(model.generate_content, **kwargs)
                    if not (isinstance(res, tuple) and res and res[0] == "__CALL_FAIL__"):
                        return res
            # if model object didn't work, keep falling back
    except Exception as e:
        # likely credentials or API mismatch — continue to other strategies
        pass

    # 2) Try the GenerativeModel class (instantiate and call generate_content)
    try:
        if hasattr(ggen, "GenerativeModel"):
            GM = ggen.GenerativeModel
            # try with model name or without args
            tried_insts = []
            for inst_args in ((), (MODEL,)):
                try:
                    inst = GM(*inst_args) if inst_args else GM()
                    tried_insts.append(inst)
                except Exception:
                    continue
            for inst in tried_insts:
                if hasattr(inst, "generate_content"):
                    for kwargs in (
                        {"input": prompt, "max_output_tokens": max_output_tokens},
                        {"prompt": prompt, "max_output_tokens": max_output_tokens},
                        {"text": prompt, "max_output_tokens": max_output_tokens},
                    ):
                        res = _try_call(inst.generate_content, **kwargs)
                        if not (isinstance(res, tuple) and res and res[0] == "__CALL_FAIL__"):
                            return res
    except Exception:
        pass

    return ("__NO_METHOD_FOUND__", "google.generativeai present but no supported generation entrypoint found")

def _use_google_genai(prompt, max_output_tokens=256):
    """
    Try google.genai (google-genai package) patterns.
    We attempt a few call shapes (generate_text, Client().generate, responses.create, etc.)
    """
    try:
        import google.genai as genai
    except Exception as e:
        return ("__NO_SDK__", f"google.genai import failed: {e}")

    # configure via environment var if needed
    try:
        if hasattr(genai, "configure"):
            genai.configure(api_key=api_key)
        else:
            os.environ["GOOGLE_API_KEY"] = api_key
    except Exception:
        pass

    # common entrypoints/patterns to attempt, in order
    # 1) top-level helper generate_text(model=..., prompt=...)
    if hasattr(genai, "generate_text"):
        try:
            r = genai.generate_text(model=MODEL, prompt=prompt, max_output_tokens=max_output_tokens)
            return r
        except Exception as e:
            # fallthrough
            pass

    # 2) genai.Client() model calls
    try:
        if hasattr(genai, "Client"):
            try:
                client = genai.Client()
                # try a few client methods (method names vary by genai version)
                for meth, kwargs in (
                    ("generate_text", {"model": MODEL, "prompt": prompt, "max_output_tokens": max_output_tokens}),
                    ("responses", {"model": MODEL, "input": prompt}),
                ):
                    if hasattr(client, meth):
                        method = getattr(client, meth)
                        try:
                            r = method(**kwargs)
                            return r
                        except Exception:
                            # try calling method() without kwargs too
                            try:
                                r = method()
                                return r
                            except Exception:
                                pass
            except Exception:
                pass
    except Exception:
        pass

    # 3) genai.responses.create(...) style
    try:
        if hasattr(genai, "responses") and hasattr(genai.responses, "create"):
            try:
                r = genai.responses.create(model=MODEL, input=prompt, max_output_tokens=max_output_tokens)
                return r
            except Exception:
                pass
    except Exception:
        pass

    return ("__NO_METHOD_FOUND__", "google.genai present but no recognized generation entrypoint available")

def _coerce_to_text(result):
    """
    Convert many possible SDK return types to a string result.
    """
    try:
        if result is None:
            return ""
        # If it's a tuple returned earlier indicating error, raise
        if isinstance(result, tuple) and result and result[0].startswith("__"):
            raise RuntimeError(f"Adapter returned: {result}")
        # If result is a dict-like with content fields
        if isinstance(result, dict):
            # common fields in different SDKs
            for path in ("candidates", "output", "content", "message", "text"):
                if path in result:
                    v = result[path]
                    # candidate lists
                    if isinstance(v, list) and v:
                        first = v[0]
                        if isinstance(first, dict) and "content" in first:
                            return first["content"]
                        return str(first)
                    return str(v)
        # If SDK returns an object with .text or .content attribute(s)
        if hasattr(result, "text"):
            return str(result.text)
        if hasattr(result, "content"):
            return str(result.content)
        if hasattr(result, "candidates"):
            try:
                cand = result.candidates[0]
                if isinstance(cand, dict) and "content" in cand:
                    return cand["content"]
                return str(cand)
            except Exception:
                pass
        # last resort: repr
        return str(result)
    except Exception as e:
        return f"<failed to coerce result: {e}>"

def generate_text(prompt, max_output_tokens=256):
    """
    Public function: returns a text string (or raises RuntimeError on fatal failures).
    """
    _ensure_key()

    # Try google.generativeai first (preferred based on probe output)
    ga_result = _use_google_generativeai(prompt, max_output_tokens=max_output_tokens)
    if not (isinstance(ga_result, tuple) and ga_result and ga_result[0].startswith("__NO")):
        # success (could return raw SDK object) -> coerce
        return _coerce_to_text(ga_result)

    # Next try google.genai
    g2 = _use_google_genai(prompt, max_output_tokens=max_output_tokens)
    if not (isinstance(g2, tuple) and g2 and g2[0].startswith("__NO")):
        return _coerce_to_text(g2)

    # If both adapters returned tuples describing the problem, raise with detail for debugging
    raise RuntimeError(f"All adapters failed. Details: generativeai={ga_result}, genai={g2}")
