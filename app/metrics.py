import threading
from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class EngineMetrics:
    requests_total: int = 0
    errors_total: int = 0
    batches_total: int = 0
    batch_sizes: list[int] = field(default_factory=list)
    inference_times: list[float] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def record_request(self) -> None:
        with self._lock:
            self.requests_total += 1

    def record_error(self, count: int = 1) -> None:
        with self._lock:
            self.errors_total += count

    def record_batch(self, batch_size: int, inference_time_seconds: float) -> None:
        with self._lock:
            self.batches_total += 1
            self.batch_sizes.append(batch_size)
            self.inference_times.append(inference_time_seconds)

    def snapshot(self, queue_size: int) -> dict:
        with self._lock:
            avg_batch_size = _average(self.batch_sizes)
            avg_inference_time = _average(self.inference_times)

            return {
                "requests_total": self.requests_total,
                "errors_total": self.errors_total,
                "queue_size": queue_size,
                "batches_total": self.batches_total,
                "batch_size": {
                    "last": self.batch_sizes[-1] if self.batch_sizes else 0,
                    "average": avg_batch_size,
                },
                "inference_time_seconds": {
                    "last": self.inference_times[-1] if self.inference_times else 0,
                    "average": avg_inference_time,
                },
            }

    def render_prometheus(self, queue_size: int) -> str:
        snapshot = self.snapshot(queue_size)
        lines = [
            "# HELP requests_total Total transcription requests accepted.",
            "# TYPE requests_total counter",
            f"requests_total {snapshot['requests_total']}",
            "# HELP errors_total Total transcription requests that failed.",
            "# TYPE errors_total counter",
            f"errors_total {snapshot['errors_total']}",
            "# HELP queue_size Current number of waiting transcription requests.",
            "# TYPE queue_size gauge",
            f"queue_size {snapshot['queue_size']}",
            "# HELP batches_total Total scheduler batches processed.",
            "# TYPE batches_total counter",
            f"batches_total {snapshot['batches_total']}",
            "# HELP batch_size Last and average scheduler batch size.",
            "# TYPE batch_size gauge",
            f"batch_size {snapshot['batch_size']['last']}",
            "# HELP batch_size_average Average scheduler batch size.",
            "# TYPE batch_size_average gauge",
            f"batch_size_average {snapshot['batch_size']['average']}",
            "# HELP inference_time_seconds Last and average batch inference time.",
            "# TYPE inference_time_seconds gauge",
            f"inference_time_seconds {snapshot['inference_time_seconds']['last']}",
            "# HELP inference_time_seconds_average Average batch inference time.",
            "# TYPE inference_time_seconds_average gauge",
            f"inference_time_seconds_average {snapshot['inference_time_seconds']['average']}",
        ]
        return "\n".join(lines) + "\n"


def _average(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)
