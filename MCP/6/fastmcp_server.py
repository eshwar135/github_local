import asyncio
import logging
from datetime import datetime
from fastmcp import FastMCP

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

mcp = FastMCP(name="fastmcp-demo", version="0.1.0")

@mcp.tool()
def hello(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool()
def add(a: float, b: float) -> float:
    return a + b

@mcp.tool()
def reverse(text: str) -> str:
    return text[::-1]

if __name__ == "__main__":
    print("🚀 FastMCP server running…")
    asyncio.run(mcp.run())
