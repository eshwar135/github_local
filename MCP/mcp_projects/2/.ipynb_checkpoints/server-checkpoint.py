# server.py
# One FastMCP server exposing tools, resources, prompts, plus progress/logging and structured output.

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TypedDict

from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP, Context, Image
from mcp.server.session import ServerSession

# In-memory todo store
from todo_store import TodoStore

# Configure logging to file
LOG_FILE = "mcp_server.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("mcp_suite")

# Server
mcp = FastMCP("MCP Suite", instructions="All-in-one FastMCP demo server.")

# Shared app context (lifespan)
@dataclass
class AppContext:
    todos: TodoStore

# Lifespan initializer for shared resources
async def _lifespan(_server: FastMCP):
    ctx = AppContext(todos=TodoStore())
    try:
        yield ctx
    finally:
        # Cleanup if needed
        pass

mcp.settings.log_level = "INFO"
mcp.settings.debug = False
mcp.settings.streamable_http_path = "/mcp"  # default

mcp.lifespan = _lifespan  # type: ignore[attr-defined]

# -------------------
# Resources
# -------------------
@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Personalized greeting"""
    msg = f"Hello, {name}! Welcome to MCP Suite."
    logger.info(f"resource:greeting name={name}")
    return msg

@mcp.resource("config://settings")
def config_settings() -> str:
    """Static configuration snippet"""
    logger.info("resource:config_settings")
    return """{
  "theme": "dark",
  "language": "en",
  "debug": false
}"""

# -------------------
# Prompts
# -------------------
@mcp.prompt(title="Greet User")
def greet_user(name: str, style: str = "friendly") -> str:
    styles = {
        "friendly": "Write a warm, friendly greeting",
        "formal": "Write a formal greeting",
        "casual": "Write a casual greeting",
    }
    logger.info(f"prompt:greet_user name={name} style={style}")
    return f"{styles.get(style, styles['friendly'])} for {name}."

@mcp.prompt(title="Code Review")
def code_review(code: str) -> str:
    logger.info("prompt:code_review")
    return f"Please review this code and suggest improvements:\n\n{code}"

# -------------------
# Tools
# -------------------
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    result = a + b
    logger.info(f"tool:add a={a} b={b} -> {result}")
    return result

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    result = a * b
    logger.info(f"tool:multiply a={a} b={b} -> {result}")
    return result

class WeatherData(BaseModel):
    temperature: float = Field(description="Temperature in Celsius")
    humidity: float = Field(description="Humidity percentage")
    condition: str
    wind_speed: float

@mcp.tool()
def get_weather(city: str) -> WeatherData:
    """Return structured weather"""
    # Demo static data; replace with real API if needed
    data = WeatherData(
        temperature=27.5,
        humidity=62.0,
        condition="partly cloudy",
        wind_speed=3.2,
    )
    logger.info(f"tool:get_weather city={city} -> {data.model_dump()}")
    return data

@mcp.tool()
async def long_running(task_name: str, steps: int = 5, ctx: Context[ServerSession, AppContext] | None = None) -> str:
    """Demonstrate progress logging"""
    logger.info(f"tool:long_running start task={task_name} steps={steps}")
    if ctx:
        await ctx.info(f"Starting: {task_name}")
    for i in range(steps):
        await asyncio.sleep(0.3)
        if ctx:
            await ctx.report_progress(progress=(i + 1) / steps, total=1.0, message=f"Step {i+1}/{steps}")
            await ctx.debug(f"Completed step {i+1}")
    logger.info(f"tool:long_running complete task={task_name}")
    return f"Task '{task_name}' completed"

# Image demo tool (no external deps required at runtime)
@mcp.tool()
def demo_image() -> Image:
    """Return a tiny 1x1 transparent PNG image"""
    # Minimal transparent pixel (precomputed)
    png_bytes = bytes.fromhex(
        "89504E470D0A1A0A0000000D49484452000000010000000108060000001F15C489"
        "0000000A49444154789C6360000002000100FF0FF30A0000000049454E44AE426082"
    )
    logger.info("tool:demo_image")
    return Image(data=png_bytes, format="png")

# In-memory TODO manager tools
@mcp.tool()
def list_tasks(ctx: Context[ServerSession, AppContext]) -> list[dict]:
    todos = ctx.request_context.lifespan_context.todos
    items = todos.list()
    logger.info(f"tool:list_tasks -> {items}")
    return items

class TaskIn(TypedDict):
    title: str
    done: bool

@mcp.tool()
def add_task(task: TaskIn, ctx: Context[ServerSession, AppContext]) -> dict:
    todos = ctx.request_context.lifespan_context.todos
    item = todos.add(task["title"], task.get("done", False))
    logger.info(f"tool:add_task -> {item}")
    return item

@mcp.tool()
def remove_task(task_id: int, ctx: Context[ServerSession, AppContext]) -> bool:
    todos = ctx.request_context.lifespan_context.todos
    ok = todos.remove(task_id)
    logger.info(f"tool:remove_task id={task_id} -> {ok}")
    return ok

# Entrypoints:
# - For Inspector over STDIO, let Inspector spawn this module (no __main__ needed).
# - For HTTP (recommended on Windows), run this file directly.

if __name__ == "__main__":
    # Rock-solid for Windows + Inspector: use Streamable HTTP
    logger.info("Starting MCP Suite (streamable-http) on http://localhost:8000/mcp")
    mcp.run(transport="streamable-http")
