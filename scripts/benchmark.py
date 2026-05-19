import argparse
import asyncio
import statistics
import time
from pathlib import Path

import httpx


async def run_request(
    client: httpx.AsyncClient,
    url: str,
    audio_path: Path,
    audio_bytes: bytes,
) -> tuple[float, int]:
    start = time.perf_counter()
    files = {
        "file": (
            audio_path.name,
            audio_bytes,
            "application/octet-stream",
        )
    }
    response = await client.post(url, files=files)
    latency = time.perf_counter() - start
    return latency, response.status_code


async def worker(
    queue: asyncio.Queue[int],
    client: httpx.AsyncClient,
    url: str,
    audio_path: Path,
    audio_bytes: bytes,
    latencies: list[float],
    statuses: list[int],
) -> None:
    while True:
        try:
            queue.get_nowait()
        except asyncio.QueueEmpty:
            return

        try:
            latency, status = await run_request(client, url, audio_path, audio_bytes)
            latencies.append(latency)
            statuses.append(status)
        finally:
            queue.task_done()


async def fetch_metrics(metrics_url: str) -> str:
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(metrics_url)
        response.raise_for_status()
        return response.text


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Benchmark concurrent /transcribe requests."
    )
    parser.add_argument("--audio", required=True, help="Path to an audio file.")
    parser.add_argument(
        "--url",
        default="http://127.0.0.1:8000/transcribe",
        help="Transcription endpoint URL.",
    )
    parser.add_argument(
        "-n",
        "--requests",
        type=int,
        default=32,
        help="Total number of requests to send.",
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=8,
        help="Number of concurrent workers.",
    )
    parser.add_argument(
        "--metrics-url",
        default=None,
        help="Optionally fetch Prometheus metrics after the run.",
    )
    args = parser.parse_args()

    audio_path = Path(args.audio)
    audio_bytes = audio_path.read_bytes()
    queue: asyncio.Queue[int] = asyncio.Queue()
    for item in range(args.requests):
        queue.put_nowait(item)

    latencies: list[float] = []
    statuses: list[int] = []
    timeout = httpx.Timeout(None)

    started = time.perf_counter()
    async with httpx.AsyncClient(timeout=timeout) as client:
        workers = [
            worker(
                queue,
                client,
                args.url,
                audio_path,
                audio_bytes,
                latencies,
                statuses,
            )
            for _ in range(args.concurrency)
        ]
        await asyncio.gather(*workers)
    total_time = time.perf_counter() - started

    successful = sum(1 for status in statuses if 200 <= status < 300)
    failed = len(statuses) - successful
    sorted_latencies = sorted(latencies)
    p50 = statistics.median(sorted_latencies) if sorted_latencies else 0
    p95 = _percentile(sorted_latencies, 95)
    average = statistics.mean(sorted_latencies) if sorted_latencies else 0
    throughput = len(statuses) / total_time if total_time > 0 else 0

    print(f"requests: {len(statuses)}")
    print(f"successful: {successful}")
    print(f"failed: {failed}")
    print(f"total_time_seconds: {total_time:.3f}")
    print(f"average_latency_seconds: {average:.3f}")
    print(f"p50_latency_seconds: {p50:.3f}")
    print(f"p95_latency_seconds: {p95:.3f}")
    print(f"throughput_requests_per_second: {throughput:.3f}")

    if args.metrics_url:
        print("\n--- metrics ---")
        print(await fetch_metrics(args.metrics_url))


def _percentile(values: list[float], percentile: int) -> float:
    if not values:
        return 0
    index = round((percentile / 100) * (len(values) - 1))
    return values[index]


if __name__ == "__main__":
    asyncio.run(main())
