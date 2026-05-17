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

- `app/main.py` owns FastAPI application setup and lifecycle.
- `app/api.py` owns HTTP endpoints: `/transcribe`, `/health`, `/metrics`, and OpenAI-style routes.
- `app/async_engine.py` owns vLLM-style scheduling concerns: queue submission, scheduler loop, dynamic batches, and response futures.
- `app/config.py` owns environment-based server configuration.
- `app/engine.py` owns model concerns: loading `WhisperModel`, wrapping it with `BatchedInferencePipeline`, and running transcription.
- `app/metrics.py` owns Prometheus metrics.
- `requirements.txt` lists runtime dependencies.

## Configuration

Environment variables:

- `WHISPER_MODEL`: model name or local CTranslate2-converted Whisper model path. Default: `small`.
- `WHISPER_DEVICE`: `cpu`, `cuda`, or another CTranslate2-supported device. Default: `cpu`.
- `WHISPER_COMPUTE_TYPE`: CTranslate2 compute type. Default: `int8`.
- `MAX_BATCH_SIZE`: maximum scheduler batch size. Default: `8`.
- `MAX_WAIT_MS`: maximum scheduler wait after the first queued request. Default: `100`.
- `QUEUE_MAX_SIZE`: maximum waiting requests before returning `429`. Default: `128`.
- `REQUEST_TIMEOUT_SECONDS`: maximum request lifetime before returning `504`. Default: `300`.
- `LOG_LEVEL`: Python logging level. Default: `INFO`.

`WHISPER_MODEL` can be either a faster-whisper model name or a local CTranslate2-converted Whisper model path.

## API

- `GET /health`: liveness and scheduler configuration.
- `GET /model`: loaded model and runtime configuration.
- `GET /v1/models`: OpenAI-style model list.
- `POST /transcribe`: upload an audio file and receive transcription JSON.
- `POST /v1/audio/transcriptions`: OpenAI-style transcription endpoint.
- `GET /metrics`: Prometheus metrics.

## Monitoring

The server exports Prometheus metrics including:

- `requests_total`
- `queue_size`
- `batch_size`
- `inference_time_seconds`
- `queue_wait_time_seconds`
- `request_latency_seconds`
- `errors_total`
- `timeouts_total`
- `rejected_requests_total`

## Run

```bash
uvicorn app.main:app --reload
```

## Docker

```bash
docker build -t faster-whisper-server .
docker run --rm -p 8000:8000 faster-whisper-server
```

Run with a local CTranslate2 model:

```bash
docker run --rm -p 8000:8000 \
  -v /path/to/ct2-model:/models/whisper \
  -e WHISPER_MODEL=/models/whisper \
  faster-whisper-server
```
