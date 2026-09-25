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
def post_chat(body: ChatRequest):
    try:
        result = handle_message(body.message)
        return {"message": body.message, "answer": result["answer"], "tool_calls": result["tool_calls"]}

    except NotImplementedError:
        return JSONResponse(
            content={
                "error": "NOT_IMPLEMENTED",
                "message": "The assistant logic in app/services/assistant_service.py hasn't been built yet.",
            },
            status_code=501,
        )

    except Exception:
        logger.exception(f"Failed to handle chat message: {body.message!r}")
        return JSONResponse(
            content={"error": "ASSISTANT_ERROR", "message": "The assistant could not process this message"},
            status_code=500,
        )
