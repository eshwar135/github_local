import asyncio
from typing import Any, Dict, Optional
import structlog

logger = structlog.get_logger()

class TokenUsage:
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_tokens = 0

    def record(self, prompt: int = 0, completion: int = 0):
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.total_tokens += (prompt + completion)

class MCPToolResult:
    def __init__(self, name: str, output: Any, meta: Optional[Dict[str, Any]] = None):
        self.name = name
        self.output = output
        self.meta = meta or {}

class MCPAgent:
    def __init__(self, tools: Dict[str, Any], llm_client: Any = None):
        self.tools = tools
        self.llm = llm_client
        self.usage = TokenUsage()

    async def decide(self, user_input: str) -> Dict[str, Any]:
        decision = {"tool": "echo", "arguments": {"text": user_input}}
        logger.info("agent_decide", decision=decision)
        self.usage.record(prompt=len(user_input.split()))
        return decision

    async def act(self, decision: Dict[str, Any]) -> MCPToolResult:
        tool_name = decision["tool"]
        args = decision.get("arguments", {})
        tool = self.tools.get(tool_name)
        if not tool:
            logger.error("tool_not_found", tool=tool_name)
            return MCPToolResult(tool_name, {"error": f"Tool '{tool_name}' not found"})
        try:
            if asyncio.iscoroutinefunction(tool):
                output = await tool(args)
            else:
                output = tool(args)
            logger.info("tool_run", tool=tool_name, args=args, output_preview=str(output)[:200])
            self.usage.record(completion=len(str(output)))
            return MCPToolResult(tool_name, output)
        except Exception as e:
            logger.exception("tool_error", tool=tool_name)
            return MCPToolResult(tool_name, {"error": str(e)})

    async def respond(self, user_input: str) -> Dict[str, Any]:
        decision = await self.decide(user_input)
        result = await self.act(decision)
        response = {
            "response": result.output,
            "decision": decision,
            "usage": {
                "prompt_tokens": self.usage.prompt_tokens,
                "completion_tokens": self.usage.completion_tokens,
                "total_tokens": self.usage.total_tokens,
            }
        }
        logger.info("agent_response", response_preview=str(response)[:300])
        return response

def echo_tool_sync(args: Dict[str, Any]) -> Dict[str, Any]:
    text = args.get("text", "")
    return {"echo": text, "length": len(text)}

async def echo_tool_async(args: Dict[str, Any]) -> Dict[str, Any]:
    await asyncio.sleep(0)
    text = args.get("text", "")
    return {"echo": text, "length": len(text)}
