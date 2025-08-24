# clients/stdio_client.py
import asyncio, os
from pydantic import AnyUrl
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=os.environ.copy(),
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            resources = await session.list_resources()
            prompts = await session.list_prompts()
            print("Tools:", [t.name for t in tools.tools])
            print("Resources:", [r.uri for r in resources.resources])
            print("Prompts:", [p.name for p in prompts.prompts])

            rr = await session.read_resource(AnyUrl("greeting://World"))
            c0 = rr.contents[0]
            if isinstance(c0, types.TextContent):
                print("Resource:", c0.text)

            result = await session.call_tool("add", {"a": 5, "b": 3})
            for c in result.content:
                if isinstance(c, types.TextContent):
                    print("add:", c.text)

asyncio.run(main())
