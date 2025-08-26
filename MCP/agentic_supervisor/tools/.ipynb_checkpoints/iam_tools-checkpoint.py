# tools/iam_tools.py
import logging

logging.basicConfig(level=logging.INFO)

# In-memory DB
users_db = {}

def create_user(username: str):
    if username in users_db:
        return f"User '{username}' already exists."
    users_db[username] = {"roles": []}
    logging.info(f"Created user: {username}")
    return f"✅ User '{username}' created successfully."

def delete_user(username: str):
    if username not in users_db:
        return f"User '{username}' does not exist."
    del users_db[username]
    logging.info(f"Deleted user: {username}")
    return f"🗑️ User '{username}' deleted successfully."

def assign_role(username: str, role: str):
    if username not in users_db:
        return f"User '{username}' does not exist."
    users_db[username]["roles"].append(role)
    logging.info(f"Assigned role {role} to {username}")
    return f"🔑 Role '{role}' assigned to '{username}'."
