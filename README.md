# faster-whisper-server

Production-style FastAPI inference server around `faster-whisper`.

## Architecture

```text
/transcribe
  -> AsyncWhisperEngine.submit
  -> asyncio.Queue
  -> scheduler loop
  -> dynamic request batch
  -> faster-whisper BatchedInferencePipeline
  -> response future
```

## Files

- `app/main.py` owns HTTP concerns: FastAPI lifecycle, `/transcribe`, `/health`, and `/metrics`.
- `app/async_engine.py` owns vLLM-style scheduling concerns: queue submission, scheduler loop, dynamic batches, and response futures.
- `app/engine.py` owns model concerns: loading `WhisperModel`, wrapping it with `BatchedInferencePipeline`, and running transcription.
- `app/metrics.py` owns lightweight in-memory metrics and Prometheus text rendering.
- `requirements.txt` lists runtime dependencies.

## Configuration

Environment variables:

- `WHISPER_MODEL`: model name or local CTranslate2-converted Whisper model path. Default: `small`.
- `WHISPER_DEVICE`: `cpu`, `cuda`, or another CTranslate2-supported device. Default: `cpu`.
- `WHISPER_COMPUTE_TYPE`: CTranslate2 compute type. Default: `int8`.
- `MAX_BATCH_SIZE`: maximum scheduler batch size. Default: `8`.
- `MAX_WAIT_MS`: maximum scheduler wait after the first queued request. Default: `100`.

## Run

```bash
uvicorn app.main:app --reload
```
