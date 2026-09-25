from mcp.server.mcpserver import MCPServer

from app.mcp_server import task_store
from app.services import google_calendar_service

mcp = MCPServer(name="TaskAssistant")


@mcp.tool()
def get_tasks() -> list[dict]:
    """Retrieve all tasks currently assigned to the user."""
    return task_store.read_tasks()


@mcp.tool()
def create_task(title: str, due_date: str) -> dict:
    """Create a new task with a title and a due date (YYYY-MM-DD)."""
    return task_store.add_task(title, due_date)


@mcp.tool()
def get_calendar_events(date: str) -> list[dict]:
    """Retrieve calendar events for a specific date (YYYY-MM-DD)."""
    return google_calendar_service.get_events(date)


@mcp.tool()
def create_calendar_event(title: str, start_time: str, end_time: str) -> dict:
    """Schedule a new calendar event (ISO 8601 start_time/end_time)."""
    return google_calendar_service.create_event(title, start_time, end_time)


if __name__ == "__main__":
    mcp.run(transport="stdio")