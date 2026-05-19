import os
import tempfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.async_engine import (
    AsyncWhisperEngine,
    QueueFullError,
    RequestTimeoutError,
    ServerShuttingDownError,
)


UPLOAD_CHUNK_SIZE = 1024 * 1024


class UploadTooLargeError(Exception):
    pass


def create_router(engine: AsyncWhisperEngine, max_upload_size_mb: int) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    def health():
        return {
            "status": "ok",
            "queue_size": engine.queue_size,
            "max_batch_size": engine.max_batch_size,
            "max_wait_ms": int(engine.max_wait_seconds * 1000),
            "max_upload_size_mb": max_upload_size_mb,
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
    async def transcribe(
        file: UploadFile = File(...),
        language: str | None = Form(default=None),
    ):
        return await _transcribe_upload(engine, file, max_upload_size_mb, language)

    @router.post("/v1/audio/transcriptions")
    async def create_transcription(
        file: UploadFile = File(...),
        model: str | None = Form(default=None),
        language: str | None = Form(default=None),
    ):
        _ = model
        return await _transcribe_upload(engine, file, max_upload_size_mb, language)

    return router


async def _transcribe_upload(
    engine: AsyncWhisperEngine,
    file: UploadFile,
    max_upload_size_mb: int,
    language: str | None,
) -> dict:
    temp_path = None
    submitted_to_engine = False

    try:
        temp_path = await _save_upload_to_temp_file(file, max_upload_size_mb)
        submitted_to_engine = True
        return await engine.transcribe(
            temp_path,
            language=_normalize_language(language),
            use_language_override=language is not None,
        )
    except UploadTooLargeError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except QueueFullError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except RequestTimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except ServerShuttingDownError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if temp_path is not None and not submitted_to_engine:
            _safe_remove(temp_path)


async def _save_upload_to_temp_file(
    file: UploadFile,
    max_upload_size_mb: int,
) -> str:
    suffix = file.filename.split(".")[-1] if file.filename else "audio"
    max_upload_bytes = max_upload_size_mb * 1024 * 1024
    bytes_written = 0

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}")
    temp_path = temp.name

    should_remove = False
    try:
        while chunk := await file.read(UPLOAD_CHUNK_SIZE):
            bytes_written += len(chunk)
            if bytes_written > max_upload_bytes:
                raise UploadTooLargeError(
                    f"upload exceeds MAX_UPLOAD_SIZE_MB={max_upload_size_mb}"
                )
            temp.write(chunk)
        return temp_path
    except Exception:
        should_remove = True
        raise
    finally:
        temp.close()
        if should_remove:
            _safe_remove(temp_path)


def _safe_remove(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def _normalize_language(language: str | None) -> str | None:
    if language is None:
        return None
    language = language.strip()
    if language == "" or language.lower() in {"auto", "model", "model_decides"}:
        return None
    return language
