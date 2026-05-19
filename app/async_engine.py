import asyncio
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional

from app.config import Settings
from app.engine import WhisperEngine
from app.metrics import EngineMetrics


logger = logging.getLogger(__name__)


class QueueFullError(Exception):
    pass


class RequestTimeoutError(Exception):
    pass


class ServerShuttingDownError(Exception):
    pass


@dataclass
class TranscriptionRequest:
    audio_path: str
    future: asyncio.Future
    submitted_at: float
    language: str | None = None
    use_language_override: bool = False


class AsyncWhisperEngine:
    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str | None = None,
        task: str = "transcribe",
        beam_size: int = 5,
        whisper_batch_size: int = 8,
        vad_filter: bool = True,
        initial_prompt: str | None = None,
        max_batch_size: int = 8,
        max_wait_ms: int = 100,
        queue_max_size: int = 128,
        request_timeout_seconds: float = 300,
        shutdown_timeout_seconds: float = 30,
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.task = task
        self.beam_size = beam_size
        self.whisper_batch_size = whisper_batch_size
        self.vad_filter = vad_filter
        self.initial_prompt = initial_prompt
        self.max_batch_size = max_batch_size
        self.max_wait_seconds = max_wait_ms / 1000
        self.queue_max_size = queue_max_size
        self.request_timeout_seconds = request_timeout_seconds
        self.shutdown_timeout_seconds = shutdown_timeout_seconds
        self.metrics = EngineMetrics()
        self._engine = WhisperEngine(
            model_size=model_size,
            device=device,
            compute_type=compute_type,
            language=language,
            task=task,
            beam_size=beam_size,
            batch_size=whisper_batch_size,
            vad_filter=vad_filter,
            initial_prompt=initial_prompt,
        )
        self._queue: asyncio.Queue[Optional[TranscriptionRequest]] = asyncio.Queue(
            maxsize=queue_max_size
        )
        self._scheduler_task: Optional[asyncio.Task] = None
        self._stopping = asyncio.Event()
        self._accepting_requests = False
        self._shutdown_started = False

    @classmethod
    def from_settings(cls, settings: Settings):
        return cls(
            model_size=settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
            language=settings.whisper_language,
            task=settings.whisper_task,
            beam_size=settings.whisper_beam_size,
            whisper_batch_size=settings.whisper_batch_size,
            vad_filter=settings.whisper_vad_filter,
            initial_prompt=settings.whisper_initial_prompt,
            max_batch_size=settings.max_batch_size,
            max_wait_ms=settings.max_wait_ms,
            queue_max_size=settings.queue_max_size,
            request_timeout_seconds=settings.request_timeout_seconds,
            shutdown_timeout_seconds=settings.shutdown_timeout_seconds,
        )

    @property
    def queue_size(self) -> int:
        return self._queue.qsize()

    def info(self) -> dict:
        return {
            "model": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "language": self.language,
            "task": self.task,
            "beam_size": self.beam_size,
            "whisper_batch_size": self.whisper_batch_size,
            "vad_filter": self.vad_filter,
            "initial_prompt_configured": self.initial_prompt is not None,
            "max_batch_size": self.max_batch_size,
            "max_wait_ms": int(self.max_wait_seconds * 1000),
            "queue_max_size": self.queue_max_size,
            "request_timeout_seconds": self.request_timeout_seconds,
            "shutdown_timeout_seconds": self.shutdown_timeout_seconds,
            "queue_size": self.queue_size,
            "batched_pipeline": self._engine.uses_batched_pipeline,
            "model_is_local": self._engine.model_is_local,
        }

    async def start(self) -> None:
        self._shutdown_started = False
        self._accepting_requests = True
        if self._scheduler_task is None or self._scheduler_task.done():
            self._stopping.clear()
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def stop(self) -> None:
        # Shutdown has three phases:
        # 1. Stop accepting new requests so no new temp files enter the queue.
        # 2. Cancel queued work that has not reached inference yet and remove files.
        # 3. Wake the scheduler, let any active batch finish, then cancel if it hangs.
        self._shutdown_started = True
        self._accepting_requests = False
        self._stopping.set()
        self._cancel_queued_requests()

        if self._scheduler_task is not None:
            await self._queue.put(None)
            try:
                await asyncio.wait_for(
                    self._scheduler_task,
                    timeout=self.shutdown_timeout_seconds,
                )
            except asyncio.TimeoutError:
                self._scheduler_task.cancel()
                try:
                    await self._scheduler_task
                except asyncio.CancelledError:
                    pass

    async def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
        use_language_override: bool = False,
    ) -> dict:
        if self._shutdown_started:
            _safe_remove(audio_path)
            raise ServerShuttingDownError("server is shutting down")

        if self._scheduler_task is None or self._scheduler_task.done():
            await self.start()

        loop = asyncio.get_running_loop()

        if not self._accepting_requests:
            _safe_remove(audio_path)
            raise ServerShuttingDownError("server is shutting down")

        future = loop.create_future()
        request = TranscriptionRequest(
            audio_path=audio_path,
            future=future,
            submitted_at=loop.time(),
            language=language,
            use_language_override=use_language_override,
        )

        if self._queue.full():
            self.metrics.record_rejection()
            _safe_remove(audio_path)
            raise QueueFullError("transcription queue is full")

        self.metrics.record_request()
        try:
            self._queue.put_nowait(request)
        except asyncio.QueueFull as exc:
            self.metrics.record_rejection()
            _safe_remove(audio_path)
            raise QueueFullError("transcription queue is full") from exc

        try:
            return await asyncio.wait_for(
                future,
                timeout=self.request_timeout_seconds,
            )
        except asyncio.TimeoutError as exc:
            future.cancel()
            self.metrics.record_timeout()
            raise RequestTimeoutError("transcription request timed out") from exc

    async def _scheduler_loop(self) -> None:
        while True:
            request = await self._get_next_active_request()
            if request is None:
                break

            batch = [request]
            deadline = asyncio.get_running_loop().time() + self.max_wait_seconds

            while len(batch) < self.max_batch_size:
                timeout = deadline - asyncio.get_running_loop().time()
                if timeout <= 0:
                    break

                try:
                    next_request = await asyncio.wait_for(
                        self._get_next_active_request(),
                        timeout,
                    )
                    if next_request is None:
                        self._stopping.set()
                        break
                    batch.append(next_request)
                except asyncio.TimeoutError:
                    break

            batch = self._drop_cancelled_requests(batch)
            if not batch:
                continue

            await self._run_batch(batch)

            if self._stopping.is_set() and self._queue.empty():
                break

    async def _get_next_active_request(self) -> Optional[TranscriptionRequest]:
        while True:
            request = await self._queue.get()
            if request is None:
                self._queue.task_done()
                return None

            if not request.future.cancelled():
                return request

            self._queue.task_done()
            _safe_remove(request.audio_path)

    def _drop_cancelled_requests(
        self,
        batch: list[TranscriptionRequest],
    ) -> list[TranscriptionRequest]:
        active_requests = []
        for request in batch:
            if request.future.cancelled():
                self._queue.task_done()
                _safe_remove(request.audio_path)
            else:
                active_requests.append(request)
        return active_requests

    async def _run_batch(self, batch: list[TranscriptionRequest]) -> None:
        start = time.perf_counter()
        loop = asyncio.get_running_loop()
        now = loop.time()

        for request in batch:
            self.metrics.record_queue_wait(now - request.submitted_at)

        try:
            results = await loop.run_in_executor(
                None,
                self._engine.transcribe_batch,
                [request.audio_path for request in batch],
                self.whisper_batch_size,
                [request.language for request in batch],
                [request.use_language_override for request in batch],
            )
            inference_time = time.perf_counter() - start
            self.metrics.record_batch(len(batch), inference_time)
            logger.info(
                "processed transcription batch",
                extra={
                    "batch_size": len(batch),
                    "inference_time_seconds": inference_time,
                },
            )

            for request, result in zip(batch, results):
                if not request.future.done():
                    if isinstance(result, Exception):
                        self.metrics.record_error()
                        logger.error("transcription request failed", exc_info=result)
                        self.metrics.record_request_latency(
                            loop.time() - request.submitted_at
                        )
                        request.future.set_exception(result)
                    else:
                        self.metrics.record_request_latency(
                            loop.time() - request.submitted_at
                        )
                        request.future.set_result(result)
        except asyncio.CancelledError as exc:
            self.metrics.record_error(len(batch))
            for request in batch:
                if not request.future.done():
                    self.metrics.record_request_latency(
                        loop.time() - request.submitted_at
                    )
                    request.future.set_exception(
                        ServerShuttingDownError("server shutdown cancelled inference")
                    )
            raise exc
        except Exception as exc:
            self.metrics.record_error(len(batch))
            logger.exception("transcription batch failed")
            for request in batch:
                if not request.future.done():
                    self.metrics.record_request_latency(
                        loop.time() - request.submitted_at
                    )
                    request.future.set_exception(exc)
        finally:
            for request in batch:
                self._queue.task_done()
                _safe_remove(request.audio_path)

    def _cancel_queued_requests(self) -> None:
        while True:
            try:
                request = self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break

            try:
                if request is None:
                    continue

                if not request.future.done():
                    self.metrics.record_error()
                    self.metrics.record_request_latency(
                        asyncio.get_running_loop().time() - request.submitted_at
                    )
                    request.future.set_exception(
                        ServerShuttingDownError("server is shutting down")
                    )
                _safe_remove(request.audio_path)
            finally:
                self._queue.task_done()


def _safe_remove(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
