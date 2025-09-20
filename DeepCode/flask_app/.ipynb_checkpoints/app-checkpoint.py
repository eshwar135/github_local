# app.py
import os
import logging
import time
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# --- Load environment variables ---
project_env = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(project_env):
    load_dotenv(project_env)

# Ensure compatibility: map GOOGLE_API_KEY -> GEMINI_API_KEY
if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
    os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# --- Adapter import ---
from adapters.gemini_adapter import GeminiAdapter

# --- Prompt service ---
from services.prompt_service import validate_and_prepare, ValidationError

# --- Configure adapter ---
api_key = os.getenv("GEMINI_API_KEY")
api_key_file = os.getenv("GEMINI_API_KEY_FILE")
adapter = GeminiAdapter(api_key=api_key, api_key_file=api_key_file)

# --- Flask app setup ---
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

# Register API blueprints (api.py already exists)
try:
    from api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    app.logger.info("Registered api blueprint at /api")
except Exception:
    app.logger.exception("Failed to register api blueprint")

# Register chat blueprint
try:
    from chat import bp as chat_bp
    app.register_blueprint(chat_bp, url_prefix="/api")
    app.logger.info("Registered chat blueprint at /api")
except Exception:
    app.logger.exception("Failed to register chat blueprint")

# --- Simple in-memory rate limiter (dev only) ---
RATE_LIMIT = {}  # ip -> list[timestamps]
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 30  # requests per window per IP

def _cleanup_timestamps(ts_list, now):
    cutoff = now - RATE_LIMIT_WINDOW
    return [t for t in ts_list if t >= cutoff]

@app.before_request
def _simple_rate_limit():
    # only limit API routes
    if not request.path.startswith("/api/"):
        return None
    ip = request.remote_addr or request.headers.get("X-Forwarded-For", "unknown")
    now = time.time()
    ts = RATE_LIMIT.get(ip, [])
    ts = _cleanup_timestamps(ts, now)
    if len(ts) >= RATE_LIMIT_MAX:
        return jsonify({"error": "rate_limited", "detail": f"max {RATE_LIMIT_MAX} requests per {RATE_LIMIT_WINDOW}s"}), 429
    ts.append(now)
    RATE_LIMIT[ip] = ts
    return None

@app.route("/api/health", methods=["GET"])
def health():
    """Health check for Gemini adapter."""
    return jsonify({"ok": True, "adapter": adapter.info()})

@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Generate text from Gemini model with validation and clamping."""
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt") or data.get("text") or ""
    max_tokens = data.get("max_output_tokens") or data.get("max_tokens")
    temperature = data.get("temperature")

    # Validate input
    try:
        prepared = validate_and_prepare(prompt, max_tokens=max_tokens, temperature=temperature)
    except ValidationError as ve:
        return jsonify({"error": "invalid_input", "detail": str(ve)}), 400

    try:
        out = adapter.generate(
            prepared["prompt"],
            max_tokens=prepared["max_tokens"],
            temperature=prepared["temperature"],
        )
        return jsonify({"output": out})
    except Exception as e:
        app.logger.exception("Generation failed")
        return jsonify({"error": "generation_failed", "detail": str(e)}), 500

if __name__ == "__main__":
    app.logger.info("Starting Flask - adapter info: %s", adapter.info())
    app.run(host="0.0.0.0", port=5000)
