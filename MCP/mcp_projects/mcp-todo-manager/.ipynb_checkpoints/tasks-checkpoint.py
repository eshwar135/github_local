# tasks.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import itertools
import threading

@dataclass
class Task:
    id: int
    title: str
    done: bool = False

class TaskStore:
    def __init__(self):
        self._lock = threading.Lock()
        self._id_counter = itertools.count(1)
        self._tasks: Dict[int, Task] = {}

    def add_task(self, title: str) -> Task:
        with self._lock:
            tid = next(self._id_counter)
            task = Task(id=tid, title=title, done=False)
            self._tasks[tid] = task
            return task

    def list_tasks(self) -> List[Task]:
        with self._lock:
            return list(self._tasks.values())

    def remove_task(self, task_id: int) -> bool:
        with self._lock:
            return self._tasks.pop(task_id, None) is not None
