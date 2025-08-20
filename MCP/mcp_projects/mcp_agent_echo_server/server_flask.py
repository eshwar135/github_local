import asyncio
from flask import Flask, request, jsonify

from app_config import SERVER_HOST, SERVER_PORT, LOG_LEVEL
from logging_setup import setup_logging
from mcp_agent import MCPAgent, echo_tool_async

logger = setup_logging(LOG_LEVEL)
app = Flask(__name__)

tools = {"echo": echo_tool_async}
agent = MCPAgent(tools=tools, llm_client=None)

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/ask")
def ask():
    try:
        data = request.get_json(force=True) or {}
        user_input = data.get("input", "")
        result = asyncio.run(agent.respond(user_input))
        return jsonify(result)
    except Exception as e:
        logger.exception("request_error")
        return jsonify({"error": str(e)}), 500

def run():
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=False)

if __name__ == "__main__":
    run()
