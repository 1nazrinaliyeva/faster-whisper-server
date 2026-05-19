import argparse
import os

import uvicorn

from app.models import BUILTIN_WHISPER_MODELS


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the faster-whisper inference server."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--log-level", default=None)
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Print built-in faster-whisper model names and exit.",
    )

    parser.add_argument("--model", dest="whisper_model", default=None)
    parser.add_argument("--device", dest="whisper_device", default=None)
    parser.add_argument("--compute-type", dest="whisper_compute_type", default=None)
    parser.add_argument("--force-language", dest="whisper_force_language", default=None)
    parser.add_argument("--task", dest="whisper_task", default=None)
    parser.add_argument("--beam-size", dest="whisper_beam_size", type=int, default=None)
    parser.add_argument(
        "--whisper-batch-size",
        dest="whisper_batch_size",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--vad-filter",
        dest="whisper_vad_filter",
        action=argparse.BooleanOptionalAction,
        default=None,
    )
    parser.add_argument(
        "--initial-prompt",
        dest="whisper_initial_prompt",
        default=None,
    )

    parser.add_argument("--max-batch-size", type=int, default=None)
    parser.add_argument("--max-wait-ms", type=int, default=None)
    parser.add_argument("--queue-max-size", type=int, default=None)
    parser.add_argument("--request-timeout-seconds", type=float, default=None)
    parser.add_argument("--shutdown-timeout-seconds", type=float, default=None)
    parser.add_argument("--max-upload-size-mb", type=int, default=None)

    args = parser.parse_args()

    if args.list_models:
        for model in BUILTIN_WHISPER_MODELS:
            print(model)
        return

    _apply_env(args)

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=(args.log_level or os.getenv("LOG_LEVEL", "info")).lower(),
    )


def _apply_env(args: argparse.Namespace) -> None:
    mappings = {
        "whisper_model": "WHISPER_MODEL",
        "whisper_device": "WHISPER_DEVICE",
        "whisper_compute_type": "WHISPER_COMPUTE_TYPE",
        "whisper_force_language": "WHISPER_FORCE_LANGUAGE",
        "whisper_task": "WHISPER_TASK",
        "whisper_beam_size": "WHISPER_BEAM_SIZE",
        "whisper_batch_size": "WHISPER_BATCH_SIZE",
        "whisper_initial_prompt": "WHISPER_INITIAL_PROMPT",
        "max_batch_size": "MAX_BATCH_SIZE",
        "max_wait_ms": "MAX_WAIT_MS",
        "queue_max_size": "QUEUE_MAX_SIZE",
        "request_timeout_seconds": "REQUEST_TIMEOUT_SECONDS",
        "shutdown_timeout_seconds": "SHUTDOWN_TIMEOUT_SECONDS",
        "max_upload_size_mb": "MAX_UPLOAD_SIZE_MB",
        "log_level": "LOG_LEVEL",
    }

    for arg_name, env_name in mappings.items():
        value = getattr(args, arg_name)
        if value is not None:
            os.environ[env_name] = str(value)

    if args.whisper_vad_filter is not None:
        os.environ["WHISPER_VAD_FILTER"] = str(args.whisper_vad_filter).lower()


if __name__ == "__main__":
    main()
