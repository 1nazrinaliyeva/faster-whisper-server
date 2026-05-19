from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from app.api import create_router
from app.async_engine import AsyncWhisperEngine
from app.config import get_settings
from app.ui import create_ui_router


settings = get_settings()
logging.basicConfig(level=settings.log_level)
engine = AsyncWhisperEngine.from_settings(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await engine.start()
    yield
    await engine.stop()


app = FastAPI(title="Faster Whisper Server", lifespan=lifespan)
app.include_router(create_ui_router())
app.include_router(create_router(engine, max_upload_size_mb=settings.max_upload_size_mb))
