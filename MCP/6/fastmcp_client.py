import asyncio
from fastmcp import FastMCP

async def main():
    client = FastMCP(name="fastmcp-client")

    # Diagnostic: list available tools
    tools = await client.get_tools()
    print("Available tools:", tools)

    hello_tool = await client.get_tool("hello")
    add_tool = await client.get_tool("add")
    reverse_tool = await client.get_tool("reverse")

    hello_result = await hello_tool.run({"name": "Zayn"})
    print("hello ->", hello_result.data)

    add_result = await add_tool.run({"a": 5, "b": 10})
    print("add ->", add_result.data)

    reverse_result = await reverse_tool.run({"text": "hello world"})
    print("reverse ->", reverse_result.data)

asyncio.run(main())
