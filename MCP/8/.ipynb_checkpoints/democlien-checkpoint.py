import asyncio
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

async def example():
    transport = StreamableHttpTransport("http://127.0.0.1:8000/mcp")
    async with Client(transport=transport) as client:
        await client.ping()
        print("Ping successful!")
        tools = await client.list_tools()
        print("Available tools:", tools)
        greeting = await client.call_tool("greet", {"name": "Alice"})
        print("Greeting result:", greeting)

if __name__ == "__main__":
    asyncio.run(example())
