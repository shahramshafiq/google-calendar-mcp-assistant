import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.services.assistant_service import handle_message

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


@router.post("/chat")
async def post_chat(body: ChatRequest):
    try:
        result = await handle_message(body.message)
        return {"message": body.message, "answer": result["answer"], "tool_calls": result["tool_calls"]}

    except Exception:
        logger.exception(f"Failed to handle chat message: {body.message!r}")
        return JSONResponse(
            content={"error": "ASSISTANT_ERROR", "message": "The assistant could not process this message"},
            status_code=500,
        )