import asyncio
from fastmcp import FastMCP

# Create MCP app instance
mcp = FastMCP(name="fastmcp-demo", version="0.1.0")

# Define tools
@mcp.tool()
def hello(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool()
def add(a: float, b: float) -> float:
    return a + b

@mcp.tool()
def reverse(text: str) -> str:
    return text[::-1]

# Async main function to run and test the tools
async def main():
    hello_tool = await mcp.get_tool("hello")
    hello_result = await hello_tool.run({"name": "Zayn"})
    print("hello ->", hello_result.content)

    add_tool = await mcp.get_tool("add")
    add_result = await add_tool.run({"a": 5, "b": 10})
    print("add ->", add_result.content)

    reverse_tool = await mcp.get_tool("reverse")
    reverse_result = await reverse_tool.run({"text": "hello world"})
    print("reverse ->", reverse_result.content)

if __name__ == "__main__":
    asyncio.run(main())
