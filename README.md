# Faster Whisper Server

A production-style inference server for `faster-whisper`.

The goal of this project is not to be a thin FastAPI wrapper. Requests go through an async queue, a scheduler, dynamic batching, faster-whisper inference, and Prometheus-compatible monitoring. The server can run built-in faster-whisper models, Hugging Face faster-whisper model ids, and local CTranslate2-converted Whisper model directories.

## What It Provides

- FastAPI server with a browser dashboard at `/`
- CLI-first startup, similar to production inference servers
- Async request queue
- Scheduler loop with dynamic batching
- Configurable batch size, wait time, queue limit, upload limit, and timeout
- faster-whisper `WhisperModel` support
- `BatchedInferencePipeline` support when available
- Local CTranslate2 model directory support
- OpenAI-style `/v1/audio/transcriptions` and `/v1/models` endpoints
- Prometheus-compatible `/metrics`
- `/health` and `/model` runtime endpoints
- Multi-file upload UI
- Benchmark script for concurrent transcription tests

## Quick Start

Clone the repository:

```bash
git clone https://github.com/1nazrinaliyeva/faster-whisper-server.git
cd faster-whisper-server
```

Install dependencies:

```bash
pip install -r requirements.txt
```

List supported built-in model names:

```bash
python3 -m app.cli --list-models
```

Run the server:

```bash
python3 -m app.cli --model large-v3-turbo --port 8000
```

Open the dashboard:

```text
http://127.0.0.1:8000/
```

Use a smaller model for faster local CPU testing:

```bash
python3 -m app.cli --model small --beam-size 1 --port 8000
```

## Docker

Build the image:

```bash
docker build -t faster-whisper-server .
```

List model names through Docker:

```bash
docker run --rm faster-whisper-server --list-models
```

Run the server:

```bash
docker run --rm -p 8000:8000 faster-whisper-server --model large-v3-turbo --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

Examples with other models:

```bash
docker run --rm -p 8000:8000 faster-whisper-server --model small --port 8000
docker run --rm -p 8000:8000 faster-whisper-server --model medium --port 8000
docker run --rm -p 8000:8000 faster-whisper-server --model large-v3 --port 8000
```

## CLI Usage

The recommended entrypoint is:

```bash
python3 -m app.cli [options]
```

Common examples:

```bash
python3 -m app.cli --list-models
python3 -m app.cli --model small
python3 -m app.cli --model large-v3-turbo --port 8000
python3 -m app.cli --model large-v3-turbo --host 0.0.0.0 --port 8000
```

Useful flags:

| Flag | Description |
| --- | --- |
| `--list-models` | Print built-in faster-whisper model names and exit. |
| `--model` | Model name, Hugging Face id, or local CT2 model path. |
| `--device` | CTranslate2 device, for example `cpu` or `cuda`. |
| `--compute-type` | Compute type, for example `int8`, `float16`, or `int8_float16`. |
| `--host` | Server host. Use `0.0.0.0` for remote access. |
| `--port` | Server port. |
| `--reload` | Enable development reload. |
| `--beam-size` | Whisper beam size. Lower is faster, higher can improve quality. |
| `--whisper-batch-size` | Internal faster-whisper batch size. |
| `--max-batch-size` | Scheduler max request batch size. |
| `--max-wait-ms` | Scheduler max wait time before running a batch. |
| `--queue-max-size` | Maximum queued requests. |
| `--request-timeout-seconds` | Request timeout. |
| `--max-upload-size-mb` | Maximum upload size. |
| `--force-language` | Optional advanced override. Leave unset so Whisper decides the language. |

By default, the model detects the audio language itself. Do not pass `--force-language` unless every uploaded audio file is known to be the same language.

## Built-In Model Names

The CLI exposes common faster-whisper model names:

```bash
python3 -m app.cli --list-models
```

Examples include:

```text
tiny
base
small
medium
large-v3
large-v3-turbo
distil-large-v3
distil-large-v3.5
```

These names are passed to faster-whisper. On first run, faster-whisper may download the model from Hugging Face and cache it locally.

## Local CTranslate2 Models

For production, a local CTranslate2-converted model directory is often better than downloading on startup.

Convert `openai/whisper-large-v3-turbo`:

```bash
pip install -U ctranslate2 transformers huggingface_hub

ct2-transformers-converter \
  --model openai/whisper-large-v3-turbo \
  --output_dir models/whisper-large-v3-turbo-ct2 \
  --copy_files tokenizer.json preprocessor_config.json \
  --quantization int8
```

Run with that local path:

```bash
python3 -m app.cli \
  --model models/whisper-large-v3-turbo-ct2 \
  --device cpu \
  --compute-type int8 \
  --port 8000
```

Docker with a local CT2 model:

```bash
docker run --rm -p 8000:8000 \
  -v "$PWD/models/whisper-large-v3-turbo-ct2:/models/whisper" \
  faster-whisper-server \
  --model /models/whisper \
  --device cpu \
  --compute-type int8 \
  --port 8000
```

A valid CT2 model directory usually contains:

```text
config.json
model.bin
tokenizer.json
preprocessor_config.json
vocabulary.json
```

If a local path does not exist, faster-whisper may treat the value as a Hugging Face repo id. Make sure the path is real before starting the server.

## Fine-Tuned Whisper Models

Fine-tuned Whisper models should be converted to CTranslate2 format first.

Example:

```bash
ct2-transformers-converter \
  --model your-org/your-whisper-finetuned-model \
  --output_dir models/your-whisper-finetuned-ct2 \
  --copy_files tokenizer.json preprocessor_config.json \
  --quantization int8
```

Run:

```bash
python3 -m app.cli \
  --model models/your-whisper-finetuned-ct2 \
  --device cpu \
  --compute-type int8 \
  --port 8000
```

For GPU:

```bash
python3 -m app.cli \
  --model models/your-whisper-finetuned-ct2 \
  --device cuda \
  --compute-type float16 \
  --port 8000
```

Language-specific fine-tuned models can still be used without forcing language. The default behavior is to let Whisper decide the audio language from the audio itself.

## Architecture

```text
/transcribe
    |
    v
chunked upload to temp file
    |
    v
AsyncWhisperEngine.transcribe()
    |
    v
asyncio.Queue
    |
    v
scheduler loop
    |
    v
dynamic batch
    |
    v
faster-whisper / BatchedInferencePipeline
    |
    v
per-request result
    |
    v
JSON response
```

Observability endpoints:

```text
/health
/model
/metrics
/
```

## Request Lifecycle

1. The client uploads an audio file to `/transcribe` or `/v1/audio/transcriptions`.
2. FastAPI streams the upload to a temporary file in chunks.
3. `MAX_UPLOAD_SIZE_MB` is enforced while streaming.
4. The temporary file path is submitted to `AsyncWhisperEngine`.
5. The request enters an `asyncio.Queue`.
6. The scheduler collects requests until `MAX_BATCH_SIZE` or `MAX_WAIT_MS`.
7. The batch is sent to faster-whisper.
8. Each request receives its own result through an `asyncio.Future`.
9. Temporary files are deleted after success, failure, timeout, rejection, or shutdown cancellation.

## API

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Browser dashboard. |
| `GET` | `/health` | Health and scheduler status. |
| `GET` | `/model` | Loaded model and runtime configuration. |
| `GET` | `/metrics` | Prometheus-compatible metrics. |
| `GET` | `/v1/models` | OpenAI-style model list. |
| `POST` | `/transcribe` | Upload one audio file for transcription. |
| `POST` | `/v1/audio/transcriptions` | OpenAI-style transcription endpoint. |

Example:

```bash
curl -F "file=@sample.wav" http://127.0.0.1:8000/transcribe
```

## Metrics

`/metrics` exports Prometheus-compatible text metrics.

Core metrics:

- `requests_total`
- `errors_total`
- `queue_size`
- `batch_size`
- `batch_size_average`
- `request_latency_seconds`
- `queue_wait_time_seconds`
- `batch_inference_time_seconds`

Additional metrics include rejected requests, timed-out requests, active requests, and processed batch counts.

## Configuration

All CLI options are also backed by environment variables.

| Variable | Default | Description |
| --- | --- | --- |
| `WHISPER_MODEL` | `small` | Model name, Hugging Face id, or local CT2 model directory. |
| `WHISPER_DEVICE` | `cpu` | CTranslate2 device. |
| `WHISPER_COMPUTE_TYPE` | `int8` | CTranslate2 compute type. |
| `WHISPER_FORCE_LANGUAGE` | empty | Optional language override. Leave empty for model language detection. |
| `WHISPER_TASK` | `transcribe` | Whisper task. |
| `WHISPER_BEAM_SIZE` | `5` | Beam size. |
| `WHISPER_BATCH_SIZE` | `8` | faster-whisper internal batch size. |
| `WHISPER_VAD_FILTER` | `true` | Enable VAD filtering. |
| `WHISPER_INITIAL_PROMPT` | empty | Optional prompt passed to Whisper. |
| `MAX_BATCH_SIZE` | `8` | Scheduler max batch size. |
| `MAX_WAIT_MS` | `100` | Scheduler max wait time in milliseconds. |
| `QUEUE_MAX_SIZE` | `128` | Maximum queued requests. |
| `REQUEST_TIMEOUT_SECONDS` | `300` | Request timeout. |
| `SHUTDOWN_TIMEOUT_SECONDS` | `30` | Graceful shutdown wait time. |
| `MAX_UPLOAD_SIZE_MB` | `512` | Maximum accepted upload size. |
| `LOG_LEVEL` | `INFO` | Python logging level. |

Environment variable example:

```bash
WHISPER_MODEL=large-v3-turbo \
WHISPER_DEVICE=cpu \
WHISPER_COMPUTE_TYPE=int8 \
python3 -m app.cli --port 8000
```

## Benchmark

Run concurrent requests:

```bash
python3 scripts/benchmark.py \
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
- throughput requests/sec
- success and failure counts
- optional metrics after the run

## Testing

Compile-check:

```bash
python3 -m compileall app scripts
```

Start locally:

```bash
python3 -m app.cli --model small --port 8000
```

Check endpoints:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/model
curl http://127.0.0.1:8000/metrics
```

Submit audio:

```bash
curl -F "file=@sample.wav" http://127.0.0.1:8000/transcribe
```

Test upload size rejection:

```bash
python3 -m app.cli --model small --max-upload-size-mb 1 --port 8000
```

Then upload a file larger than 1 MB and expect HTTP `413`.

## Project Files

| File | Purpose |
| --- | --- |
| `app/main.py` | FastAPI app creation and lifespan startup/shutdown. |
| `app/api.py` | API routes and chunked upload handling. |
| `app/ui.py` | Browser dashboard. |
| `app/cli.py` | CLI entrypoint for model and server configuration. |
| `app/models.py` | Built-in model name list for CLI display. |
| `app/config.py` | Environment-based configuration. |
| `app/engine.py` | faster-whisper model loading and inference. |
| `app/async_engine.py` | Async queue, scheduler, batching, futures, and graceful shutdown. |
| `app/metrics.py` | Prometheus-compatible metrics rendering. |
| `scripts/benchmark.py` | Concurrent request benchmark. |
| `Dockerfile` | Container image with CLI entrypoint. |
| `requirements.txt` | Runtime dependencies. |

## Current Limitations

- This is vLLM-style scheduling for audio requests, not vLLM token-level continuous batching.
- faster-whisper still performs transcription per audio file; `BatchedInferencePipeline` batches internal audio chunks when available.
- The OpenAI-compatible endpoint supports the common `file` and `model` fields, but not every OpenAI audio parameter yet.
- One process loads one model and runs one scheduler loop.
- Long CTranslate2 inference calls may not stop instantly during shutdown; the server waits, then cancels pending queued work safely.
