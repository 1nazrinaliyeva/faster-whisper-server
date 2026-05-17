import tempfile
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse

from app.async_engine import AsyncWhisperEngine


engine = AsyncWhisperEngine(
    model_size=os.getenv("WHISPER_MODEL", "small"),
    device=os.getenv("WHISPER_DEVICE", "cpu"),
    compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
    max_batch_size=int(os.getenv("MAX_BATCH_SIZE", "8")),
    max_wait_ms=int(os.getenv("MAX_WAIT_MS", "100")),
)


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


@app.get("/metrics", response_class=PlainTextResponse)
def metrics():
    return engine.metrics.render_prometheus(queue_size=engine.queue_size)

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    suffix = file.filename.split(".")[-1] if file.filename else "audio"

    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as temp:
        temp.write(await file.read())
        temp_path = temp.name

    try:
        return await engine.transcribe(temp_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
