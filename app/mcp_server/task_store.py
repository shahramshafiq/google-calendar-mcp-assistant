"""
CORE LOGIC, TODO: simple JSON-file-backed storage for tasks.

data/tasks.json currently holds: {"tasks": []}

Suggested shape for one task dict: {"id": ..., "title": ..., "due_date": ..., "created_at": ...}
Keep it plain: read the whole file, modify the list in memory, write the whole file back.
No database needed for this project.

Functions the MCP tools in server.py will need from this module:
"""

from app.config import settings


def read_tasks() -> list[dict]:
    """Read and return the full list of tasks from settings.task_store_path."""
    raise NotImplementedError


def add_task(title: str, due_date: str) -> dict:
    """Create a new task dict, append it to the stored list, save, and return the new task."""
    raise NotImplementedError
