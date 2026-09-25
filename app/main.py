import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routes import chat
from app.utils.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"Starting Task Assistant, using model {settings.openai_model}")
    # TODO once the MCP client is built in assistant_service.py: start the MCP server
    # subprocess and open the ClientSession here, so it's reused across requests instead
    # of relaunching the subprocess on every single chat message.
    yield
    logger.info("Application shutting down")


app = FastAPI(title="MCP Task Assistant", lifespan=lifespan)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unexpected error handling {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        content={"error": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred"},
        status_code=500,
    )


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(chat.router)

# Mounted last and at "/": the explicit /health and /chat routes above are matched first,
# anything else falls through to serving the frontend's static files.
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
