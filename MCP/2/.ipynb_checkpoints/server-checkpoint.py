from mcp.server.fastmcp import FastMCP

server = FastMCP("example-server")

@server.tool()
def hello(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    server.run()

