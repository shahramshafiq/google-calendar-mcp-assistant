import json
from datetime import datetime

from openai import AsyncOpenAI

from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

MAX_TOOL_ROUNDS = 4

SYSTEM_PROMPT_TEMPLATE = """You are a helpful assistant that manages the user's tasks and Google Calendar.

Today's date and time is: {now}. Use this to resolve relative dates like "today", "tomorrow", or
"next Friday" into real calendar dates.

You have exactly 4 tools available: viewing tasks, creating a task, viewing calendar events on a
date, and creating a calendar event. You cannot do anything outside of these 4 actions, for example
you cannot delete a task or edit an existing calendar event. If asked to do something like that,
say so honestly instead of pretending to do it.

If a required detail is missing or genuinely ambiguous (an unclear date, a task with no title, an
event with no time), ask the user a clarifying question instead of guessing.

If you try to book a calendar event and are told there is a scheduling conflict, explain the
conflict clearly to the user and ask what they'd like to do instead, do not silently pick a
different time on your own."""

_session = None


def set_session(session):
    global _session
    _session = session


async def get_openai_tools():
    mcp_tools = await _session.list_tools()
    return [
        {"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.input_schema}}
        for t in mcp_tools.tools
    ]


async def handle_message(user_message: str) -> dict:
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(now=datetime.now().strftime("%A, %Y-%m-%d %H:%M"))
    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]
    tools = await get_openai_tools()
    tool_calls_made = []

    for _ in range(MAX_TOOL_ROUNDS):
        response = await client.chat.completions.create(model=settings.openai_model, messages=messages, tools=tools)
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            print(messages)
            return {"answer": message.content, "tool_calls": tool_calls_made}

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            tool_calls_made.append(name)
            print(f"LLM decided to call: {name}({args})")

            try:
                result = await _session.call_tool(name, args)
                result_text = result.content[0].text if result.content else "[]"
            except Exception as e:
                result_text = f"Error calling {name}: {e}"

            print(f"Tool result: {result_text}")

            messages.append({"role": "tool", "tool_call_id": call.id, "content": result_text})

    return {"answer": "Sorry, I couldn't complete this request.", "tool_calls": tool_calls_made}