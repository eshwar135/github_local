# state.py
from typing import Dict, Any

class AgentState:
    def __init__(self):
        self.memory: Dict[str, Any] = {}
        self.logs: list[str] = []
    
    def log(self, message: str):
        self.logs.append(message)
    
    def get_logs(self):
        return "\n".join(self.logs)
