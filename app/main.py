from contextlib import asynccontextmanager
import logging
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.async_engine import AsyncWhisperEngine, QueueFullError, RequestTimeoutError
from app.config import get_settings


settings = get_settings()
logging.basicConfig(level=settings.log_level)
engine = AsyncWhisperEngine.from_settings(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await engine.start()
    yield
    await engine.stop()


app = FastAPI(title="Faster Whisper Server", lifespan=lifespan)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "queue_size": engine.queue_size,
        "max_batch_size": engine.max_batch_size,
        "max_wait_ms": int(engine.max_wait_seconds * 1000),
    }


@app.get("/model")
def model_info():
    return engine.info()


@app.get("/v1/models")
def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": engine.model_size,
                "object": "model",
                "owned_by": "faster-whisper-server",
            }
        ],
    }


@app.get("/metrics")
def metrics():
    return Response(
        content=engine.metrics.render_prometheus(queue_size=engine.queue_size),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    return await _transcribe_upload(file)


@app.post("/v1/audio/transcriptions")
async def create_transcription(
    file: UploadFile = File(...),
    model: str | None = Form(default=None),
):
    _ = model
    return await _transcribe_upload(file)


async def _transcribe_upload(file: UploadFile) -> dict:
    suffix = file.filename.split(".")[-1] if file.filename else "audio"

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as temp:
        temp.write(await file.read())
        temp_path = temp.name

    try:
        return await engine.transcribe(temp_path)
    except QueueFullError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except RequestTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
