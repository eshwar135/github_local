MCP Suite (All-in-One)
======================

Setup (PowerShell):
  python -m venv .venv
  . .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt

Run (Streamable HTTP, recommended):
  . .\.venv\Scripts\Activate.ps1
  python server.py
  # Inspector: Transport = Streamable HTTP, URL = http://localhost:8000/mcp

Optional (STDIO):
  Use Inspector STDIO with:
    Command: python
    Arguments: server.py
  or run clients\stdio_client.py

Tools:
  - add(a,b), multiply(a,b), long_running(task_name,steps), get_weather(city),
    list_tasks(), add_task({title,done}), remove_task(task_id)

Resources:
  - greeting://{name}, config://settings

Prompts:
  - Greet User, Code Review

Logs:
  - mcp_server.log
