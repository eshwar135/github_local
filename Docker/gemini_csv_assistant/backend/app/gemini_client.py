import os
import re
from typing import Dict

# Try to use Google's official genai client if available, otherwise fall back to requests
try:
    from google import genai  # official Google Generative AI Python client
    _HAS_GENAI = True
except Exception:
    import requests
    _HAS_GENAI = False

MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5")
API_KEY = os.environ.get("GEMINI_API_KEY")


def _extract_python_code(text: str) -> str:
    """Extract a python code block from text (```python ... ``` or ``` ... ```)."""
    m = re.search(r"```(?:python)?\n([\s\S]*?)```", text)
    if m:
        return m.group(1).strip()
    return ""


def ask_gemini_for_code(prompt: dict) -> Dict[str, str]:
    """
    Call Gemini 1.5 and return a dict with 'pandas_code' and 'explanation'.

    prompt: { 'filename': '/path/to/csv', 'user_query': '...' }
    """
    if not API_KEY:
        # No API key -> fall back to local default so the app still runs for demo
        return {
            "pandas_code": "# No GEMINI_API_KEY set - default preview\noutput = df.head(10)\n",
            "explanation": "GEMINI_API_KEY not set. Returned a local default snippet.",
        }

    user_q = prompt.get("user_query", "")
    filename = prompt.get("filename", "<unknown csv>")

    system_prompt = (
        "You are a helpful assistant that returns two things: (1) a short natural-language explanation, "
        "and (2) a Python/pandas snippet that assigns the final result to a variable named `output`. "
        "The snippet must assume `df` is preloaded (pandas DataFrame). Return code enclosed in triple backticks. "
        "Keep code minimal and safe (only use pandas/numpy)."
    )

    full_prompt = (
        f"{system_prompt}\n\nCSV_FILE: {filename}\nUSER_QUERY: {user_q}\n\n"
        "Respond with an explanation and a python code block that sets `output`."
    )

    text = ""
    # 1) Use official client if available
    if _HAS_GENAI:
        try:
            try:
                genai.configure(api_key=API_KEY)
                client = genai.Client()
            except Exception:
                client = genai.Client(api_key=API_KEY)
            resp = client.models.generate_content(model=MODEL, contents=full_prompt)
            text = getattr(resp, "text", None) or str(resp)
        except Exception as e:
            text = f"Error calling genai client: {e}"
    else:
        # Fallback: REST call (may need to adapt auth for your Google setup)
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        }
        body = {
            "prompt": {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"CSV_FILE: {filename}\nUSER_QUERY: {user_q}"},
                ]
            },
            "temperature": 0.2,
            "maxOutputTokens": 1024,
        }
        try:
            r = requests.post(endpoint, headers=headers, json=body, timeout=30)
            r.raise_for_status()
            j = r.json()
            if isinstance(j, dict):
                if "candidates" in j and len(j["candidates"]) > 0:
                    text = j["candidates"][0].get("content", "")
                elif "outputs" in j and len(j["outputs"]) > 0:
                    text = j["outputs"][0].get("content", "")
                elif "response" in j:
                    text = str(j["response"])
                else:
                    text = str(j)
            else:
                text = str(j)
        except Exception as e:
            text = f"Error calling REST endpoint: {e} - {getattr(r, 'text', '')}"

    # Extract python code
    code = _extract_python_code(text)
    explanation = text

    if not code:
        default = "# Default: return first 10 rows\noutput = df.head(10)\n"
        return {"pandas_code": default, "explanation": explanation}

    # Ensure `output` exists
    if "output" not in code and "return" not in code:
        code = (
            code
            + "\n# Ensure final result is assigned to `output`.\n"
            "try:\n"
            "    output\n"
            "except NameError:\n"
            "    output = locals().get('result', locals().get('df', None))\n"
            "    if hasattr(output, 'head'):\n"
            "        output = output.head(10)\n"
            "    else:\n"
            "        output = df.head(10)\n"
        )

    return {"pandas_code": code, "explanation": explanation}
