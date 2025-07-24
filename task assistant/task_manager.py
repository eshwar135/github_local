import json
from typing import List, Dict

class TaskManager:
    def __init__(self, file_path: str = "tasks.json"):
        self.file_path = file_path
        self.tasks: List[Dict] = self.load_tasks()

    def load_tasks(self) -> List[Dict]:
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_tasks(self):
        with open(self.file_path, "w") as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, title: str, category: str, priority: int):
        task = {
            "title": title,
            "category": category,
            "priority": priority,
            "status": "pending"
        }
        self.tasks.append(task)
        self.save_tasks()

    def complete_task(self, index: int):
        if 0 <= index < len(self.tasks):
            self.tasks[index]["status"] = "completed"
            self.save_tasks()

    def get_tasks_by_category(self, category: str) -> List[Dict]:
        if category == "All":
            return self.tasks
        return [t for t in self.tasks if t["category"] == category]

    def clear_tasks(self):
        self.tasks = []
        self.save_tasks()
