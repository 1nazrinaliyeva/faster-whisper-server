import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    whisper_model: str = "small"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    whisper_language: str | None = None
    whisper_task: str = "transcribe"
    whisper_beam_size: int = 5
    whisper_batch_size: int = 8
    whisper_vad_filter: bool = True
    whisper_initial_prompt: str | None = None
    max_batch_size: int = 8
    max_wait_ms: int = 100
    queue_max_size: int = 128
    request_timeout_seconds: float = 300
    shutdown_timeout_seconds: float = 30
    max_upload_size_mb: int = 512
    log_level: str = "INFO"


def get_settings() -> Settings:
    return Settings(
        whisper_model=os.getenv("WHISPER_MODEL", "small"),
        whisper_device=os.getenv("WHISPER_DEVICE", "cpu"),
        whisper_compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
        whisper_language=_get_optional_str("WHISPER_FORCE_LANGUAGE"),
        whisper_task=os.getenv("WHISPER_TASK", "transcribe"),
        whisper_beam_size=_get_int("WHISPER_BEAM_SIZE", 5),
        whisper_batch_size=_get_int("WHISPER_BATCH_SIZE", 8),
        whisper_vad_filter=_get_bool("WHISPER_VAD_FILTER", True),
        whisper_initial_prompt=_get_optional_str("WHISPER_INITIAL_PROMPT"),
        max_batch_size=_get_int("MAX_BATCH_SIZE", 8),
        max_wait_ms=_get_int("MAX_WAIT_MS", 100),
        queue_max_size=_get_int("QUEUE_MAX_SIZE", 128),
        request_timeout_seconds=_get_float("REQUEST_TIMEOUT_SECONDS", 300),
        shutdown_timeout_seconds=_get_float("SHUTDOWN_TIMEOUT_SECONDS", 30),
        max_upload_size_mb=_get_int("MAX_UPLOAD_SIZE_MB", 512),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    return int(value)


def _get_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    return float(value)


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _get_optional_str(name: str) -> str | None:
    value = os.getenv(name)
    if value is None or value == "" or value.lower() in {"auto", "model", "model_decides"}:
        return None
    return value
