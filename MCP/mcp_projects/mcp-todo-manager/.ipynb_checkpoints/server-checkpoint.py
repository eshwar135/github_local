# server.py
import os
import json
from typing import Any, Dict
from fastmcp import FastMCP, Tool, ToolParam, TextContent, JSONSchema
from tasks import TaskStore

# Optional: verbose logs during dev
VERBOSE = os.environ.get("MCP_VERBOSE", "0") == "1"

app = FastMCP(
    name="mcp-todo-manager",
    version="0.1.0",
    description="A simple MCP server managing in-memory todos with add/list/remove tools.",
)

store = TaskStore()

@app.tool(
    name="add_task",
    description="Add a new todo task by title, returns the created task {id, title, done}.",
    input_schema=JSONSchema(
        type="object",
        properties={
            "title": {"type": "string", "description": "Title/summary for the task"},
        },
        required=["title"],
        additionalProperties=False,
    ),
)
def add_task_tool(params: Dict[str, Any]):
    title = params["title"].strip()
    if not title:
        raise ValueError("title must be non-empty")
    task = store.add_task(title)
    return {
        "id": task.id,
        "title": task.title,
        "done": task.done,
    }

@app.tool(
    name="list_tasks",
    description="List all tasks as an array of {id, title, done}.",
    input_schema=JSONSchema(
        type="object",
        properties={},
        additionalProperties=False,
    ),
)
def list_tasks_tool(params: Dict[str, Any]):
    tasks = store.list_tasks()
    return [
        {"id": t.id, "title": t.title, "done": t.done}
    ] if tasks else []

@app.tool(
    name="remove_task",
    description="Remove a task by integer id. Returns {removed: bool}.",
    input_schema=JSONSchema(
        type="object",
        properties={
            "id": {"type": "integer", "description": "Task id to remove"},
        },
        required=["id"],
        additionalProperties=False,
    ),
)
def remove_task_tool(params: Dict[str, Any]):
    tid = int(params["id"])
    removed = store.remove_task(tid)
    return {"removed": removed}

if __name__ == "__main__":
    # Start stdio server for MCP clients (Claude Desktop / Inspector)
    # FastMCP runs stdio by default when invoked as a script.
    # However, for direct uvicorn HTTP debugging, uncomment below.
    #
    # import uvicorn
    # uvicorn.run(app.http_app(), host="127.0.0.1", port=8080)
    app.run_stdio(verbose=VERBOSE)
