import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    whisper_model: str = "small"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    max_batch_size: int = 8
    max_wait_ms: int = 100
    queue_max_size: int = 128
    request_timeout_seconds: float = 300
    log_level: str = "INFO"


def get_settings() -> Settings:
    return Settings(
        whisper_model=os.getenv("WHISPER_MODEL", "small"),
        whisper_device=os.getenv("WHISPER_DEVICE", "cpu"),
        whisper_compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8"),
        max_batch_size=_get_int("MAX_BATCH_SIZE", 8),
        max_wait_ms=_get_int("MAX_WAIT_MS", 100),
        queue_max_size=_get_int("QUEUE_MAX_SIZE", 128),
        request_timeout_seconds=_get_float("REQUEST_TIMEOUT_SECONDS", 300),
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
