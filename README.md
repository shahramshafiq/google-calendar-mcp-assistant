# MCP Task Assistant

An AI assistant that manages tasks and real Google Calendar events through exactly 4 MCP tools. Ask it things like "show me my pending tasks" or "book a meeting tomorrow at 3 PM", it reasons about which of its 4 tools to use, calls them for real through the Model Context Protocol, and replies in plain language.

## Architecture

```
Browser (frontend/)
      |
      v
FastAPI  POST /chat  (app/routes/chat.py)
      |
      v
assistant_service.py -- the orchestration loop
      |         |
      v         v
conversation_memory.py   mcp_client.py -- talks to the MCP server
  (remembers the              |
   conversation)          stdio transport
                               |
                               v
                    mcp_server/server.py
                    (the real, separate MCP server process,
                     launched once at startup, kept alive
                     for the app's whole lifetime)
                          /            \
                 task_store.py    google_calendar_service.py
                 (local JSON       (real Google Calendar API,
                  file)             with conflict checking)
```

The assistant never calls the 4 tools directly. It goes through a real MCP client talking, over
the actual MCP protocol (stdio transport), to a separate MCP server process, exactly the
User → LLM/assistant → MCP client → MCP server → tools diagram the assignment itself describes.

## The 4 MCP tools

| Tool | Description | Parameters | Returns |
|---|---|---|---|
| `get_tasks` | Retrieve all tasks currently assigned to the user | none | list of `{id, title, due_date}` |
| `create_task` | Create a new task | `title: str`, `due_date: str` (YYYY-MM-DD) | the created task |
| `get_calendar_events` | Retrieve calendar events for a specific date | `date: str` (YYYY-MM-DD) | list of `{id, title, start, end}` |
| `create_calendar_event` | Schedule a new calendar event, checks for a scheduling conflict first and refuses to double-book | `title: str`, `start_time: str`, `end_time: str` (ISO 8601) | `{"booked": true, ...}` on success, or `{"booked": false, "conflict": {...}}` if the slot is already taken |

Every tool's schema (name, description, parameter types) is generated automatically from its
Python type hints and docstring in `app/mcp_server/server.py`, that's what an MCP client reads
to know what's available and how to call it, nothing is hardcoded on the assistant's side.

## Example request flows (tested live against the real running app)

**"Show me my tasks and tomorrow's calendar events."** The assistant recognizes this is really
two separate requests bundled together, calls `get_tasks` and `get_calendar_events` (resolving
"tomorrow" using the real current date and time, injected fresh into every request), and combines
both results into one answer:
```
Here are your tasks:
1. Test task, due on 2026-10-01
2. Complete project MCP Task Assistant, due today (2026-09-26)
3. test task 2, due tomorrow (2026-09-27)

For tomorrow's calendar events (2026-09-27), you have:
- "test task 3" from 12:11 PM to 1:11 PM (local time).
```

**"Book a meeting called Team Sync on October 1st 2026 from 3 PM to 3:30 PM"**, a time slot
that's already booked. `create_calendar_event` checks for a conflict before creating anything,
finds one, and does **not** double-book:
```
There is a scheduling conflict with another event titled "Test Event" on October 1st, 2026,
from 3 PM to 3:30 PM. Would you like to pick a different time for the "Team Sync" meeting or
do something else?
```

## Error handling

- **A tool fails or times out:** caught in `mcp_client.call_tool()`, the error is fed back to
  the model as a normal observation (not a crash), and the model explains the problem to the
  user in plain language instead of the request failing outright.
- **A required parameter is missing** (no task title, no event time): the system prompt
  (`app/services/prompts.py`) instructs the model to ask a clarifying question rather than guess.
- **An ambiguous date/time:** same, the model is told to ask rather than silently pick one
  interpretation. The real current date and time are injected into the system prompt on every
  single message, the model has no clock of its own, so "tomorrow" and "next Friday" resolve
  correctly and stay accurate no matter how long the app has been running.
- **A scheduling conflict:** `create_calendar_event` always checks the target time slot before
  booking, never after. If something's already there, it refuses to create the event and reports
  the conflict instead of double-booking, verified live above.
- **An unsupported request** (e.g. "delete this task"): the system prompt explicitly states the
  4 tools' real boundaries, the model says so honestly instead of pretending to comply.
- **Any unhandled error anywhere in the request:** caught by a global FastAPI exception handler
  (`app/main.py`), returned as a consistent `{"error": "...", "message": "..."}` shape instead of
  a raw stack trace reaching the client.

## Setup

1. Create the venv and install dependencies:
   ```bash
   python -m venv venv
   venv/Scripts/pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and add your OpenAI API key.
3. For Google Calendar: create a project in Google Cloud Console, enable the Calendar API,
   create OAuth 2.0 credentials (Desktop app), download as `credentials/credentials.json`.
   The first real run opens a browser to authorize access, and remembers it afterward via
   `credentials/token.json`.

## Running

```bash
venv/Scripts/uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` for the testing frontend. `POST /chat` is the API itself, body
shape `{"message": "..."}`, returns `{"answer": ..., "tool_calls": [...]}`.

## Project structure

- `app/main.py` — FastAPI app; connects to the MCP server once at startup (`AsyncExitStack`)
  and keeps that one connection alive for the app's whole lifetime, rather than reconnecting
  per message.
- `app/routes/chat.py` — the one API endpoint, `POST /chat`.
- `app/services/assistant_service.py` — the orchestration loop: ask the LLM, call tools through
  MCP if it asks to, feed results back, repeat until there's a final answer (bounded, so it can
  never loop forever).
- `app/services/mcp_client.py` — everything about talking to the MCP server: holding the
  connection, converting its tools into OpenAI's function-calling format, calling a tool and
  safely handling its result.
- `app/services/conversation_memory.py` — remembers the conversation across separate messages.
- `app/services/prompts.py` — the system prompt, including the assistant's real boundaries and
  its error-handling instructions.
- `app/services/google_calendar_service.py` — real Google Calendar API calls, including the
  OAuth login flow and the pre-booking conflict check.
- `app/mcp_server/server.py` — the actual MCP server, exposing the 4 tools.
- `app/mcp_server/task_store.py` — simple JSON-file storage for tasks (`data/tasks.json`).
- `frontend/` — the plain HTML/CSS/JS testing UI, no framework, served directly by FastAPI.

## Testing the MCP server on its own

```bash
venv/Scripts/python.exe -m app.mcp_server.server
```
Should start and wait on stdio without crashing (Ctrl+C to stop). Run it with `-m`, not as a
plain script, the absolute imports need the project root on the path, which only `-m` gives you.
