"""
CORE LOGIC, TODO: the actual AI assistant. This is the piece the whole assignment is
really about, User -> LLM -> MCP client -> MCP server -> tools, all wired together here.

Suggested flow for handle_message(user_message):
1. Start (or reuse) an MCP ClientSession connected to app/mcp_server/server.py over
   stdio, the exact same pattern as Desktop/AI-Agents-MCP-Learning/mcp-demo/client.py
   (StdioServerParameters + stdio_client + ClientSession).
2. Call session.list_tools() to get the 4 tools' real schemas, no need to hardcode them.
3. Convert those MCP tool schemas into OpenAI's "tools" function-calling format, and call
   settings.openai_model (gpt-4.1-mini) with the user's message plus that tools list.
4. If the model's response asks to call one or more tools, call each one for real via
   session.call_tool(name, arguments), one MCP call per tool the model chose.
5. Feed the tool result(s) back to the model as the tool role, ask it for a final,
   natural-language answer.
6. Return the final answer, plus which tool(s) were actually called, so the frontend
   can display both (useful for testing and for the assignment's own requirement to
   "explain how the assistant identifies the correct tool").

Keep an eye on error handling here specifically (Task 4 of the assignment): a tool
raising an exception, a missing required argument, or an ambiguous date should all be
handled explicitly, not just let an exception bubble up as a generic 500.
"""


def handle_message(user_message: str) -> dict:
    """
    Process one user message end to end and return {"answer": str, "tool_calls": list[str]}.
    tool_calls should list the MCP tool names that were actually invoked (empty list if none).
    """
    raise NotImplementedError
