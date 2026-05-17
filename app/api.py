import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.async_engine import AsyncWhisperEngine, QueueFullError, RequestTimeoutError


def create_router(engine: AsyncWhisperEngine) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health():
        return {
            "status": "ok",
            "queue_size": engine.queue_size,
            "max_batch_size": engine.max_batch_size,
            "max_wait_ms": int(engine.max_wait_seconds * 1000),
        }

    @router.get("/model")
    def model_info():
        return engine.info()

    @router.get("/v1/models")
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

    @router.get("/metrics")
    def metrics():
        return Response(
            content=engine.metrics.render_prometheus(queue_size=engine.queue_size),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    @router.post("/transcribe")
    async def transcribe(file: UploadFile = File(...)):
        return await _transcribe_upload(engine, file)

    @router.post("/v1/audio/transcriptions")
    async def create_transcription(
        file: UploadFile = File(...),
        model: str | None = Form(default=None),
    ):
        _ = model
        return await _transcribe_upload(engine, file)

    return router


async def _transcribe_upload(engine: AsyncWhisperEngine, file: UploadFile) -> dict:
    temp_path = await _save_upload_to_temp_file(file)

    try:
        return await engine.transcribe(temp_path)
    except QueueFullError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except RequestTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


async def _save_upload_to_temp_file(file: UploadFile) -> str:
    suffix = file.filename.split(".")[-1] if file.filename else "audio"

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as temp:
        temp.write(await file.read())
        return temp.name
