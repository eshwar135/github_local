from fastmcp import FastMCP, tool
import asyncio
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastMCP(
    name="fastmcp-demo",
    version="0.1.0",
    description="A minimal MCP server with a few tools."
)

@tool
def hello(name: str) -> str:
    logging.info("hello() called with name=%s", name)
    return f"Hello, {name}!"

@tool
def add(a: float, b: float) -> float:
    logging.info("add() called with a=%s b=%s", a, b)
    return a + b

@tool
def reverse(text: str) -> str:
    logging.info("reverse() called")
    return text[::-1]

@app.resource("time://now")
def current_time() -> str:
    return datetime.now().isoformat()

@app.prompt("greet")
def greet_prompt():
    return {
        "description": "A simple greeting prompt",
        "messages": [
            {"role": "system", "content": "You are a friendly greeter."},
            {"role": "user", "content": "Say hello in a nice way."}
        ]
    }

if __name__ == "__main__":
    logging.info("Starting FastMCP server on stdio… waiting for client")
    asyncio.run(app.run())
