# graph.py
from langgraph.graph import StateGraph, END
from models.ollama_llm import query_ollama
from tools import iam_tools
import json

def build_graph():
    workflow = StateGraph(dict)  # Use dict as state

    def supervisor_node(state):
        logs = state.get("logs", [])
        logs.append("🤖 Running supervisor reasoning via LLM...")
        query = state.get("memory", {}).get("query", "")  # Correctly get query string

        prompt = f"""
You are an IAM automation assistant.
Your job is to decide what function to call for a user's IAM request.

Return ONLY a single JSON object, with this schema:

{{
  "action": string,       // one of "create_user", "delete_user", "assign_role", or "respond"
  "args": object,         // dict of arguments for the function
  "message": string       // human-readable message for user
}}

DO NOT include any Python code, markdown, explanations, or anything else.

Examples:

User request: Create a new IAM user Alice
Response:
{{
  "action": "create_user",
  "args": {{"username": "Alice"}},
  "message": "User 'Alice' created successfully."
}}

User request: Assign role admin to Bob
Response:
{{
  "action": "assign_role",
  "args": {{"username": "Bob", "role": "admin"}},
  "message": "Role 'admin' assigned to 'Bob'."
}}

User request: Delete user Carol
Response:
{{
  "action": "delete_user",
  "args": {{"username": "Carol"}},
  "message": "User 'Carol' deleted."
}}

User request: {query}
Response:
"""
        response = query_ollama(prompt)
        memory = state.get("memory", {})
        memory["llm_response"] = response
        return {"memory": memory, "logs": logs}

    def executor_node(state):
        logs = state.get("logs", [])
        memory = state.get("memory", {})
        response = memory.get("llm_response", "")
        logs.append(f"LLM raw output: {response}")

        action, args, message = "respond", {}, "Unable to interpret."
        try:
            parsed = json.loads(response)
            action = parsed.get("action", "respond")
            args = parsed.get("args", {})
            message = parsed.get("message", "")
        except json.JSONDecodeError:
            logs.append("⚠️ Could not parse JSON, defaulting to respond.")

        result = message
        if action == "create_user":
            result = iam_tools.create_user(args.get("username", "unknown"))
        elif action == "delete_user":
            result = iam_tools.delete_user(args.get("username", "unknown"))
        elif action == "assign_role":
            result = iam_tools.assign_role(args.get("username", "unknown"), args.get("role", "user"))

        memory["result"] = result
        return {"memory": memory, "logs": logs}

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("executor", executor_node)

    workflow.add_edge("supervisor", "executor")
    workflow.set_entry_point("supervisor")
    workflow.add_edge("executor", END)

    return workflow.compile()
