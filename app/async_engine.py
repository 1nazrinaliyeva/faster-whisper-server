import asyncio
import os
import time
from dataclasses import dataclass
from typing import Optional

from app.engine import WhisperEngine
from app.metrics import EngineMetrics


@dataclass
class TranscriptionRequest:
    audio_path: str
    future: asyncio.Future
    submitted_at: float


class AsyncWhisperEngine:
    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        max_batch_size: int = 8,
        max_wait_ms: int = 100,
    ):
        self.max_batch_size = max_batch_size
        self.max_wait_seconds = max_wait_ms / 1000
        self.metrics = EngineMetrics()
        self._engine = WhisperEngine(
            model_size=model_size,
            device=device,
            compute_type=compute_type,
        )
        self._queue: asyncio.Queue[TranscriptionRequest] = asyncio.Queue()
        self._scheduler_task: Optional[asyncio.Task] = None
        self._stopping = asyncio.Event()

    @property
    def queue_size(self) -> int:
        return self._queue.qsize()

    async def start(self) -> None:
        if self._scheduler_task is None or self._scheduler_task.done():
            self._stopping.clear()
            self._scheduler_task = asyncio.create_task(self._scheduler_loop())

    async def stop(self) -> None:
        self._stopping.set()
        if self._scheduler_task is not None:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass

    async def transcribe(self, audio_path: str) -> dict:
        await self.start()
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        request = TranscriptionRequest(
            audio_path=audio_path,
            future=future,
            submitted_at=loop.time(),
        )

        self.metrics.record_request()
        await self._queue.put(request)
        return await future

    async def _scheduler_loop(self) -> None:
        while not self._stopping.is_set():
            request = await self._queue.get()
            batch = [request]
            deadline = asyncio.get_running_loop().time() + self.max_wait_seconds

            while len(batch) < self.max_batch_size:
                timeout = deadline - asyncio.get_running_loop().time()
                if timeout <= 0:
                    break

                try:
                    batch.append(await asyncio.wait_for(self._queue.get(), timeout))
                except asyncio.TimeoutError:
                    break

            await self._run_batch(batch)

    async def _run_batch(self, batch: list[TranscriptionRequest]) -> None:
        start = time.perf_counter()
        loop = asyncio.get_running_loop()

        try:
            results = await loop.run_in_executor(
                None,
                self._engine.transcribe_batch,
                [request.audio_path for request in batch],
                len(batch),
            )
            inference_time = time.perf_counter() - start
            self.metrics.record_batch(len(batch), inference_time)

            for request, result in zip(batch, results):
                if not request.future.done():
                    if isinstance(result, Exception):
                        self.metrics.record_error()
                        request.future.set_exception(result)
                    else:
                        request.future.set_result(result)
        except Exception as exc:
            self.metrics.record_error(len(batch))
            for request in batch:
                if not request.future.done():
                    request.future.set_exception(exc)
        finally:
            for request in batch:
                self._queue.task_done()
                _safe_remove(request.audio_path)


def _safe_remove(path: str) -> None:
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
