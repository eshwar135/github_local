from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from app_config import SERVER_HOST, SERVER_PORT, LOG_LEVEL
from logging_setup import setup_logging
from mcp_agent import MCPAgent, echo_tool_async

logger = setup_logging(LOG_LEVEL)
app = FastAPI(title="MCP Agent Echo Server (FastAPI)")

tools = {"echo": echo_tool_async}
agent = MCPAgent(tools=tools, llm_client=None)

class AskPayload(BaseModel):
    input: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask(payload: AskPayload):
    try:
        result = await agent.respond(payload.input)
        return result
    except Exception as e:
        logger.exception("request_error")
        raise HTTPException(status_code=500, detail=str(e))

def run():
    uvicorn.run(app, host=SERVER_HOST, port=SERVER_PORT)

if __name__ == "__main__":
    run()
