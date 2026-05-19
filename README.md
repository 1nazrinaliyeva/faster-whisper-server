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
| `WHISPER_FORCE_LANGUAGE` | empty | Optional advanced override, for example `az`, `en`, or `tr`. Leave empty so Whisper chooses the audio language itself. |
| `WHISPER_TASK` | `transcribe` | Whisper task, usually `transcribe` or `translate`. |
| `WHISPER_BEAM_SIZE` | `5` | Beam size used by faster-whisper. Higher can improve quality, lower is faster. |
| `WHISPER_BATCH_SIZE` | `8` | Internal faster-whisper batched pipeline size. |
| `WHISPER_VAD_FILTER` | `true` | Enable or disable faster-whisper VAD filtering. |
| `WHISPER_INITIAL_PROMPT` | empty | Optional prompt for domain/language hints. |
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

`/path/to/ct2-model` in examples is only a placeholder. Replace it with a real directory on your machine. If the directory does not exist, `faster-whisper` may try to interpret the value as a Hugging Face repo id.

The CT2 model directory should contain files such as:

```text
config.json
model.bin
tokenizer.json
preprocessor_config.json
vocabulary.json
```

CPU example:

```bash
WHISPER_MODEL=models/whisper-large-v3-turbo-ct2-int8 \
WHISPER_DEVICE=cpu \
WHISPER_COMPUTE_TYPE=int8 \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Fine-Tuned Whisper Models

The server is designed to run any Whisper-compatible model that `faster-whisper` can load. In practice, production deployments should use CTranslate2 format.

If you have a fine-tuned Hugging Face Whisper model, convert it first:

```bash
ct2-transformers-converter \
  --model your-org/your-whisper-finetuned-model \
  --output_dir models/your-whisper-finetuned-ct2 \
  --copy_files tokenizer.json preprocessor_config.json \
  --quantization int8
```

Then run the server with that local path:

```bash
WHISPER_MODEL=models/your-whisper-finetuned-ct2 \
WHISPER_TASK=transcribe \
WHISPER_BEAM_SIZE=5 \
WHISPER_BATCH_SIZE=8 \
WHISPER_VAD_FILTER=true \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Do not set `WHISPER_FORCE_LANGUAGE` if you want Whisper to choose the language for each audio file. Set it only when all uploaded audio is known to be the same language.

For GPU:

```bash
WHISPER_MODEL=models/your-whisper-finetuned-ct2 \
WHISPER_DEVICE=cuda \
WHISPER_COMPUTE_TYPE=float16 \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For language-specific fine-tuned models, set `WHISPER_FORCE_LANGUAGE` only when every input is expected to be that language. Leave it empty when Whisper should choose the language itself.

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

Recommended CLI entrypoint:

```bash
python -m app.cli --model large-v3-turbo --host 0.0.0.0 --port 8000
```

List built-in faster-whisper model names:

```bash
python -m app.cli --list-models
```

Use any listed model with `--model`:

```bash
python -m app.cli --model small
python -m app.cli --model medium
python -m app.cli --model large-v3
python -m app.cli --model large-v3-turbo
```

Faster local testing:

```bash
python -m app.cli \
  --model small \
  --beam-size 1 \
  --max-batch-size 2 \
  --request-timeout-seconds 900 \
  --reload
```

Run with a local CT2 model path:

```bash
python -m app.cli \
  --model models/whisper-large-v3-turbo-ct2 \
  --device cpu \
  --compute-type int8 \
  --host 0.0.0.0 \
  --port 8000
```

Advanced language override is optional. By default, Whisper chooses the audio language itself:

```bash
python -m app.cli --model large-v3-turbo
```

Force one language only when every input is known to be that language:

```bash
python -m app.cli --model large-v3-turbo --force-language az
```

The environment-variable style still works:

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
docker run --rm faster-whisper-server --list-models
docker run --rm -p 8000:8000 faster-whisper-server --model large-v3-turbo --port 8000
```

The Docker image uses the same CLI flags as the local command. Pick any model from
`--list-models` and pass it with `--model`:

```bash
docker run --rm -p 8000:8000 faster-whisper-server --model small --port 8000
docker run --rm -p 8000:8000 faster-whisper-server --model medium --port 8000
docker run --rm -p 8000:8000 faster-whisper-server --model large-v3 --port 8000
```

Run Docker with a local CTranslate2 model:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/models/whisper-large-v3-turbo-ct2:/models/whisper" \
  faster-whisper-server \
  --model /models/whisper \
  --device cpu \
  --compute-type int8 \
  --port 8000
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
