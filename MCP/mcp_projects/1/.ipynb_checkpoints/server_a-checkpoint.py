from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo A")

@mcp.tool()
def add(a: int, b: int) -> int:
    "Add two numbers"
    return a + b

@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    "Personalized greeting"
    return f"Hello, {name}!"

@mcp.prompt()
def greet_user(name: str, style: str = "friendly") -> str:
    styles = {
        "friendly": "Write a warm, friendly greeting",
        "formal": "Write a formal, professional greeting",
        "casual": "Write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for {name}."
