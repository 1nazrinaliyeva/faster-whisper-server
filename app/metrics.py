from dataclasses import dataclass, field

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest


@dataclass(init=False)
class EngineMetrics:
    registry: CollectorRegistry = field(default_factory=CollectorRegistry)

    def __init__(self):
        self.registry = CollectorRegistry()
        self.requests_total = Counter(
            "requests_total",
            "Total transcription requests accepted.",
            registry=self.registry,
        )
        self.errors_total = Counter(
            "errors_total",
            "Total transcription requests that failed.",
            registry=self.registry,
        )
        self.timeouts_total = Counter(
            "timeouts_total",
            "Total transcription requests that timed out.",
            registry=self.registry,
        )
        self.rejected_requests_total = Counter(
            "rejected_requests_total",
            "Total transcription requests rejected before queueing.",
            registry=self.registry,
        )
        self.batches_total = Counter(
            "batches_total",
            "Total scheduler batches processed.",
            registry=self.registry,
        )
        self.queue_size = Gauge(
            "queue_size",
            "Current number of waiting transcription requests.",
            registry=self.registry,
        )
        self.active_requests = Gauge(
            "active_requests",
            "Current number of accepted requests waiting for a response.",
            registry=self.registry,
        )
        self.batch_size = Histogram(
            "batch_size",
            "Scheduler batch size.",
            buckets=(1, 2, 4, 8, 16, 32),
            registry=self.registry,
        )
        self.inference_time_seconds = Histogram(
            "inference_time_seconds",
            "Batch inference time in seconds.",
            buckets=(0.1, 0.5, 1, 2.5, 5, 10, 30, 60, 120),
            registry=self.registry,
        )
        self.queue_wait_time_seconds = Histogram(
            "queue_wait_time_seconds",
            "Time spent waiting in the scheduler queue.",
            buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
            registry=self.registry,
        )
        self.request_latency_seconds = Histogram(
            "request_latency_seconds",
            "End-to-end request latency in seconds.",
            buckets=(0.1, 0.5, 1, 2.5, 5, 10, 30, 60, 120, 300),
            registry=self.registry,
        )

    def record_request(self) -> None:
        self.requests_total.inc()
        self.active_requests.inc()

    def record_error(self, count: int = 1) -> None:
        self.errors_total.inc(count)

    def record_batch(self, batch_size: int, inference_time_seconds: float) -> None:
        self.batches_total.inc()
        self.batch_size.observe(batch_size)
        self.inference_time_seconds.observe(inference_time_seconds)

    def record_queue_wait(self, queue_wait_seconds: float) -> None:
        self.queue_wait_time_seconds.observe(queue_wait_seconds)

    def record_request_latency(self, request_latency_seconds: float) -> None:
        self.request_latency_seconds.observe(request_latency_seconds)
        self.active_requests.dec()

    def record_timeout(self) -> None:
        self.timeouts_total.inc()
        self.active_requests.dec()

    def record_rejection(self) -> None:
        self.rejected_requests_total.inc()

    def render_prometheus(self, queue_size: int) -> bytes:
        self.queue_size.set(queue_size)
        return generate_latest(self.registry)
