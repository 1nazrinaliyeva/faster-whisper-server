# faster-whisper-server

Production-style FastAPI inference server around `faster-whisper`, with an async request queue, dynamic batching scheduler, Prometheus metrics, a small browser dashboard, and support for local CTranslate2-converted Whisper model directories.

## Architecture

```text
client
  -> POST /transcribe or /v1/audio/transcriptions
  -> chunked upload to temporary file
  -> AsyncWhisperEngine.transcribe()
  -> asyncio.Queue
  -> scheduler loop
  -> dynamic request batch
  -> faster-whisper WhisperModel / BatchedInferencePipeline
  -> per-request Future
  -> JSON response

observability
  -> GET /health
  -> GET /model
  -> GET /metrics
  -> GET /
```

## Request Lifecycle

1. FastAPI receives an audio upload.
2. The upload is streamed to a temporary file in chunks instead of reading the whole file into memory.
3. `MAX_UPLOAD_SIZE_MB` is enforced while streaming. If the limit is exceeded, the temporary file is deleted and HTTP `413` is returned.
4. The temporary file path is submitted to `AsyncWhisperEngine`.
5. The engine rejects new requests when the queue is full or the server is shutting down.
6. The scheduler collects queued requests up to `MAX_BATCH_SIZE` or `MAX_WAIT_MS`.
7. The batch is executed through faster-whisper. If `BatchedInferencePipeline` is available, it is used.
8. Each request receives its own result through an `asyncio.Future`.
9. Temporary files are deleted after completion, timeout, queue rejection, shutdown cancellation, or inference error.

## Files

- `app/main.py` owns FastAPI application setup and lifecycle.
- `app/api.py` owns HTTP endpoints and chunked upload handling.
- `app/ui.py` owns the browser dashboard at `/`.
- `app/async_engine.py` owns queueing, scheduling, batching, request futures, shutdown behavior, and temp-file cleanup.
- `app/config.py` owns environment-based server configuration.
- `app/engine.py` owns `WhisperModel` loading and faster-whisper inference.
- `app/metrics.py` owns Prometheus-compatible metrics.
- `scripts/benchmark.py` runs concurrent transcription benchmarks.
- `requirements.txt` lists runtime dependencies.

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `WHISPER_MODEL` | `small` | faster-whisper model name or local CTranslate2 model directory. |
| `WHISPER_DEVICE` | `cpu` | CTranslate2 device, for example `cpu` or `cuda`. |
| `WHISPER_COMPUTE_TYPE` | `int8` | CTranslate2 compute type, for example `int8`, `float16`, or `int8_float16`. |
| `MAX_BATCH_SIZE` | `8` | Maximum scheduler batch size. |
| `MAX_WAIT_MS` | `100` | Maximum scheduler wait after the first queued request. |
| `QUEUE_MAX_SIZE` | `128` | Maximum queued requests before returning HTTP `429`. |
| `REQUEST_TIMEOUT_SECONDS` | `300` | Maximum request lifetime before returning HTTP `504`. |
| `SHUTDOWN_TIMEOUT_SECONDS` | `30` | Time to wait for active scheduler work during shutdown before cancellation. |
| `MAX_UPLOAD_SIZE_MB` | `512` | Maximum accepted upload size before returning HTTP `413`. |
| `LOG_LEVEL` | `INFO` | Python logging level. |

## CT2 Model Conversion

`WHISPER_MODEL` can point directly to a local CTranslate2-converted Whisper model directory. This is the recommended path for production because the server can start without downloading model weights.

Install conversion dependencies:

```bash
pip install -U ctranslate2 transformers huggingface_hub
```

Convert `openai/whisper-large-v3-turbo`:

```bash
ct2-transformers-converter \
  --model openai/whisper-large-v3-turbo \
  --output_dir models/whisper-large-v3-turbo-ct2 \
  --copy_files tokenizer.json preprocessor_config.json \
  --quantization float16
```

For CPU-only deployment, use an int8 conversion:

```bash
ct2-transformers-converter \
  --model openai/whisper-large-v3-turbo \
  --output_dir models/whisper-large-v3-turbo-ct2-int8 \
  --copy_files tokenizer.json preprocessor_config.json \
  --quantization int8
```

Run the server with the local model path:

```bash
WHISPER_MODEL=models/whisper-large-v3-turbo-ct2 \
WHISPER_DEVICE=cuda \
WHISPER_COMPUTE_TYPE=float16 \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

CPU example:

```bash
WHISPER_MODEL=models/whisper-large-v3-turbo-ct2-int8 \
WHISPER_DEVICE=cpu \
WHISPER_COMPUTE_TYPE=int8 \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API

- `GET /`: browser dashboard for uploads, runtime status, and metrics.
- `GET /health`: liveness and scheduler configuration.
- `GET /model`: loaded model and runtime configuration.
- `GET /v1/models`: OpenAI-style model list.
- `POST /transcribe`: upload an audio file and receive transcription JSON.
- `POST /v1/audio/transcriptions`: OpenAI-style transcription endpoint.
- `GET /metrics`: Prometheus metrics.

Example:

```bash
curl -F "file=@sample.wav" http://127.0.0.1:8000/transcribe
```

## Monitoring

`/metrics` is Prometheus-compatible and exports:

- `requests_total`
- `errors_total`
- `queue_size`
- `batch_size`
- `batch_size_average`
- `request_latency_seconds`
- `queue_wait_time_seconds`
- `batch_inference_time_seconds`

Additional operational metrics include rejected requests, timeouts, active requests, and total processed batches.

## Run

```bash
uvicorn app.main:app --reload
```

Open the dashboard:

```text
http://127.0.0.1:8000/
```

## Docker

```bash
docker build -t faster-whisper-server .
docker run --rm -p 8000:8000 faster-whisper-server
```

Run Docker with a local CTranslate2 model:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/models/whisper-large-v3-turbo-ct2:/models/whisper" \
  -e WHISPER_MODEL=/models/whisper \
  -e WHISPER_DEVICE=cpu \
  -e WHISPER_COMPUTE_TYPE=int8 \
  faster-whisper-server
```

## Benchmark

Run `N` requests with `C` concurrent workers:

```bash
python scripts/benchmark.py \
  --audio sample.wav \
  --url http://127.0.0.1:8000/transcribe \
  --requests 32 \
  --concurrency 8 \
  --metrics-url http://127.0.0.1:8000/metrics
```

The benchmark prints:

- total time
- average latency
- p50 latency
- p95 latency
- throughput in requests/sec
- success/failure counts
- optional Prometheus metrics after the run

## Testing

Compile-check the app:

```bash
python -m compileall app scripts
```

Start the server:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Check health and model configuration:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/model
curl http://127.0.0.1:8000/metrics
```

Submit a transcription:

```bash
curl -F "file=@sample.wav" http://127.0.0.1:8000/transcribe
```

Test upload limit behavior:

```bash
MAX_UPLOAD_SIZE_MB=1 uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Then upload a file larger than 1 MB and expect HTTP `413`.

## Current Limitations

- Server-level batching groups client requests for scheduling, but faster-whisper still transcribes each audio file independently.
- `BatchedInferencePipeline` batches internal audio chunks when available; it is not the same as vLLM token-level continuous batching.
- The OpenAI-compatible endpoint accepts the common `file` and `model` fields, but advanced OpenAI parameters are not implemented yet.
- There is one scheduler loop and one loaded model per process.
- In-flight CTranslate2 inference cannot always be interrupted immediately; shutdown waits for active work before cancellation.
