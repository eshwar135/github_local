from flask import Blueprint, request, jsonify, current_app
import google.generativeai as ggen
from adapters.gemini_adapter_helper import generate_from_model

bp = Blueprint("api", __name__)

@bp.route("/generate", methods=["POST"])
def generate():
    payload = request.get_json(force=True)
    prompt = payload.get("prompt") or payload.get("text") or ""
    model_name = current_app.config.get("GEMINI_MODEL", "gemini-1.5-flash")
    # get the model object (ggen should already be configured at app startup)
    model = ggen.get_model(model_name)
    result = generate_from_model(model, prompt, max_output_tokens=150)
    if result.get("ok"):
        return jsonify({"output": result["text"], "debug": result["debug"]})
    return jsonify({"error": f"GeminiAdapter call failed: {result.get('error')}", "debug": result.get("debug")}), 500
