# todo_store.py
from __future__ import annotations

class TodoStore:
    def __init__(self):
        self._items: list[dict] = []
        self._next_id = 1

    def list(self) -> list[dict]:
        return list(self._items)

    def add(self, title: str, done: bool = False) -> dict:
        item = {"id": self._next_id, "title": title, "done": bool(done)}
        self._next_id += 1
        self._items.append(item)
        return item

    def remove(self, task_id: int) -> bool:
        idx = next((i for i, it in enumerate(self._items) if it["id"] == task_id), -1)
        if idx >= 0:
            self._items.pop(idx)
            return True
        return False
