import json
import uuid

from app.config import settings


def read_tasks() -> list[dict]:
    with open(settings.task_store_path, encoding="utf-8") as f:
        data = json.load(f)
    return data["tasks"]


def add_task(title: str, due_date: str) -> dict:
    tasks = read_tasks()

    new_task = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "due_date": due_date,
    }
    tasks.append(new_task)

    with open(settings.task_store_path, "w", encoding="utf-8") as f:
        json.dump({"tasks": tasks}, f, indent=2)

    return new_task