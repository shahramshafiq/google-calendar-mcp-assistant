"""
CORE LOGIC, TODO: the real MCP server, exposing the 4 tools this assignment requires.

The decorator API is already correct and matches the working demo in
Desktop/AI-Agents-MCP-Learning/mcp-demo/server.py, note the class is MCPServer
(not FastMCP, that name was renamed in this SDK version), imported from
mcp.server.mcpserver.

Each tool below just needs its body filled in, calling the matching function from
task_store.py or google_calendar_service.py. The type hints and docstrings you see
are what MCP turns into the tool's schema automatically, keep them accurate.

Run this file on its own to sanity-check it starts: venv/Scripts/python.exe -m app.mcp_server.server
"""

from mcp.server.mcpserver import MCPServer

from app.mcp_server import task_store
from app.services import google_calendar_service

mcp = MCPServer(name="TaskAssistant")


@mcp.tool()
def get_tasks() -> list[dict]:
    """Retrieve all tasks currently assigned to the user."""
    raise NotImplementedError  # TODO: return task_store.read_tasks()


@mcp.tool()
def create_task(title: str, due_date: str) -> dict:
    """Create a new task with a title and a due date (YYYY-MM-DD)."""
    raise NotImplementedError  # TODO: return task_store.add_task(title, due_date)


@mcp.tool()
def get_calendar_events(date: str) -> list[dict]:
    """Retrieve calendar events for a specific date (YYYY-MM-DD)."""
    raise NotImplementedError  # TODO: return google_calendar_service.get_events(date)


@mcp.tool()
def create_calendar_event(title: str, start_time: str, end_time: str) -> dict:
    """Schedule a new calendar event (ISO 8601 start_time/end_time)."""
    raise NotImplementedError  # TODO: return google_calendar_service.create_event(title, start_time, end_time)


if __name__ == "__main__":
    mcp.run(transport="stdio")
