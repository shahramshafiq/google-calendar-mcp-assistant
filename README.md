# MCP Task Assistant

An AI assistant that manages tasks and Google Calendar events through 4 MCP tools
(`get_tasks`, `create_task`, `get_calendar_events`, `create_calendar_event`), built as a small MCP project.

## Architecture

```
Browser (frontend/)  -->  FastAPI (/chat)  -->  assistant_service.py  -->  MCP client
                                                                              |
                                                                         stdio transport
                                                                              |
                                                                    mcp_server/server.py
                                                                   (the real MCP server)
                                                                              |
                                                          task_store.py / google_calendar_service.py
```

The assistant never calls the 4 tools directly, it goes through a real MCP client talking
to a real, separate MCP server process, exactly as the assignment's own architecture
diagram describes.

## What's built vs. what's left (TODO)

**Built:** FastAPI app (`app/main.py`), settings (`app/config.py`), logging, the `/chat`
route with error handling, the complete frontend, folder structure, dependencies.

**TODO, on purpose, this is the actual assignment:**
- `app/mcp_server/server.py`: fill in the 4 `@mcp.tool()` function bodies.
- `app/mcp_server/task_store.py`: simple JSON-file read/write for tasks.
- `app/services/google_calendar_service.py`: real Google Calendar API calls.
- `app/services/assistant_service.py`: the actual LLM + MCP orchestration, this is the
  core of the whole assignment. Detailed steps are in that file's docstring.

## Setup

1. Create the venv and install dependencies:
   ```bash
   python -m venv venv
   venv/Scripts/pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your OpenAI API key.
3. For Google Calendar: create a project in Google Cloud Console, enable the Calendar API,
   create OAuth 2.0 credentials (Desktop app), download as `credentials/credentials.json`.
   The first real run will open a browser to authorize access.

## Running

```bash
venv/Scripts/uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` for the testing frontend. `POST /chat` is the API itself.

Until `assistant_service.py` is implemented, the frontend works end to end but `/chat`
returns a clear `501 NOT_IMPLEMENTED` response, so you can verify the whole wiring (UI,
routing, error handling) before writing any of the core logic.

## Testing the MCP server on its own

```bash
venv/Scripts/python.exe -m app.mcp_server.server
```
Should start and wait on stdio without crashing (Ctrl+C to stop), confirms the server
itself is valid before wiring the client up to it. Run it with `-m`, not as a plain
script, the absolute imports (`from app.config import ...`) need the project root on
the path, which only `-m` gives you.
