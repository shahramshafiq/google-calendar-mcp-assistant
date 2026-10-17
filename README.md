<div align="center">

# MCP Task Assistant

A chat assistant that reads and books Google Calendar events and manages a task list through its own MCP server.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-stdio-5A4FCF?style=flat-square)
![OpenAI](https://img.shields.io/badge/OpenAI-gpt--4.1--mini-412991?style=flat-square&logo=openai&logoColor=white)
![Google Calendar](https://img.shields.io/badge/Google%20Calendar-API%20v3-4285F4?style=flat-square&logo=googlecalendar&logoColor=white)

</div>

## Overview

This project lets you manage a task list and a Google Calendar in plain language, for example "show me my pending tasks" or "book a meeting tomorrow at 3 PM". A FastAPI backend sends each message to an OpenAI model, which decides which of four tools to call. The tools run in a separate MCP server process that the backend talks to over the Model Context Protocol (stdio transport), and the model turns the results into a plain-language reply.

## Key Features

- **Real MCP architecture:** the FastAPI app starts the MCP server as a subprocess once at startup and keeps one `ClientSession` open for the lifetime of the app (`app/main.py`).
- **Four tools, no hardcoded schemas:** `get_tasks`, `create_task`, `get_calendar_events` and `create_calendar_event` are registered in `app/mcp_server/server.py`. The assistant reads the tool list from the MCP server and converts it to OpenAI function-calling format at request time (`app/services/mcp_client.py`).
- **Conflict-safe booking:** `create_calendar_event` lists events in the requested slot before inserting anything and returns `booked: false` with the first clashing event's title and times instead of double-booking.
- **Bounded tool-calling loop:** the model can call tools for at most 4 rounds per message (`MAX_TOOL_ROUNDS`), then the service returns a fallback reply.
- **Date-aware prompts:** the current date and time are injected into the system prompt on every message, so "tomorrow" and "next Friday" resolve correctly. The prompt also tells the model to ask when a title, date or time is missing, and to say so honestly when asked for something outside the four tools.
- **Graceful failures:** a failing tool call is returned to the model as an observation rather than crashing the request (`call_tool`), and a global FastAPI handler returns a consistent `{"error": ..., "message": ...}` JSON shape.
- **Google OAuth with token caching:** the first calendar call runs the installed-app OAuth flow and saves `credentials/token.json`; later runs reuse and refresh it.
- **Built-in test UI:** a plain HTML, CSS and JavaScript chat page served by FastAPI that shows which tools were used for each reply.

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python (backend), JavaScript, HTML and CSS (frontend) |
| Web framework | FastAPI, Uvicorn |
| Protocol | Model Context Protocol Python SDK (`mcp` 2.2.0), stdio transport |
| LLM | OpenAI Chat Completions with tool calling, default model `gpt-4.1-mini` |
| Calendar | Google Calendar API v3 (`google-api-python-client`, `google-auth-oauthlib`) |
| Configuration | pydantic-settings (loads `.env`) |
| Storage | Local JSON file for tasks (`data/tasks.json`) |

## Project Structure

```text
app/
  main.py                      FastAPI app, starts the MCP server and holds the client session
  config.py                    Settings loaded from .env
  routes/chat.py               POST /chat endpoint
  services/
    assistant_service.py       LLM tool-calling loop
    mcp_client.py              MCP session wrapper, tool list and tool calls
    conversation_memory.py     In-memory chat history
    prompts.py                 System prompt
    google_calendar_service.py Calendar API calls, OAuth flow, conflict check
  mcp_server/
    server.py                  MCP server exposing the four tools
    task_store.py              JSON-file task storage (data/tasks.json)
frontend/                      Plain HTML/CSS/JS chat UI
credentials/                   Google OAuth client file and token (both git-ignored)
```

## Getting Started

### Prerequisites

- Windows with Python 3 and pip. The backend launches the MCP server with `venv/Scripts/python.exe` (see `app/main.py`), so the virtual environment must be named `venv`, and the app must be started from the project root (the `frontend`, `data` and `credentials` paths are relative too).
- An OpenAI API key.
- A Google Cloud project with the Calendar API enabled and an OAuth 2.0 client ID of type Desktop app.

### Installation

```powershell
python -m venv venv
venv\Scripts\pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set the variables below. `OPENAI_MODEL` defaults to `gpt-4.1-mini` in code, so set it to a real model name or delete the placeholder line.

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `OPENAI_MODEL` | No | Chat model name (default `gpt-4.1-mini`) |
| `GOOGLE_CREDENTIALS_PATH` | No | OAuth client file (default `credentials/credentials.json`) |
| `GOOGLE_TOKEN_PATH` | No | Saved OAuth token (default `credentials/token.json`) |
| `TASK_STORE_PATH` | No | Task file (default `data/tasks.json`) |

Download your OAuth client as `credentials/credentials.json`. The first calendar request opens a browser window to authorize access and then writes `credentials/token.json`.

### Run

```powershell
venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Open `http://localhost:8000` for the chat UI.

## Usage

Try messages such as:

- "Show me my pending tasks"
- "What meetings do I have tomorrow?"
- "Add a task to submit the report, due 2026-11-02"
- "Book Team Sync on 1 November 2026 from 3 PM to 3:30 PM" (if the slot is taken, the assistant reports the conflict and asks what to do instead)

The chat endpoint can also be called directly:

```text
POST /chat
{"message": "show me my pending tasks"}

200: {"message": "...", "answer": "...", "tool_calls": ["get_tasks"]}
500: {"error": "ASSISTANT_ERROR", "message": "The assistant could not process this message"}
```

`GET /health` returns `{"status": "healthy"}`.

The MCP server can also be started on its own to check that it boots and waits on stdio (run it with `-m` from the project root, because the imports need the project root on the path, and keep `.env` in place because the settings load at import):

```powershell
venv\Scripts\python.exe -m app.mcp_server.server
```

### MCP tools

| Tool | Parameters | Returns |
|---|---|---|
| `get_tasks` | none | List of `{id, title, due_date}` |
| `create_task` | `title`, `due_date` (YYYY-MM-DD) | The created task |
| `get_calendar_events` | `date` (YYYY-MM-DD) | List of `{id, title, start, end}` |
| `create_calendar_event` | `title`, `start_time`, `end_time` (ISO 8601) | `{"booked": true, ...}` or `{"booked": false, "conflict": {...}}` |

## Limitations and Roadmap

- The MCP server path is hardcoded to `venv/Scripts/python.exe`, so setup is Windows-only for now. Using `sys.executable` would make it portable.
- Conversation history is one shared in-memory list that grows without limit and resets on restart. There are no per-user sessions yet.
- The calendar timezone is fixed to `Asia/Karachi` in `google_calendar_service.py`, and any offset in the supplied ISO time is replaced by it.
- There are no automated tests, and the assistant cannot edit or delete tasks and events.

## Author

**Shahram Shafiq** - [GitHub](https://github.com/shahramshafiq) | [LinkedIn](https://www.linkedin.com/in/shahramshafiq/)
