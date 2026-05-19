import os

from faster_whisper import WhisperModel

try:
    from faster_whisper import BatchedInferencePipeline
except ImportError:
    BatchedInferencePipeline = None


class WhisperEngine:
    def __init__(self, model_size="small", device="cpu", compute_type="int8"):
        self.model_name_or_path = model_size
        self.model_is_local = os.path.isdir(model_size)
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        self.pipeline = (
            BatchedInferencePipeline(model=self.model)
            if BatchedInferencePipeline is not None
            else self.model
        )
        self.uses_batched_pipeline = BatchedInferencePipeline is not None

    def transcribe(self, audio_path: str, batch_size: int = 8):
        if self.uses_batched_pipeline:
            segments, info = self.pipeline.transcribe(
                audio_path,
                beam_size=5,
                batch_size=batch_size,
            )
        else:
            segments, info = self.pipeline.transcribe(audio_path, beam_size=5)
        text = " ".join(segment.text for segment in segments)

        return {
            "text": text,
            "language": info.language,
            "duration": info.duration
        }

    def transcribe_batch(self, audio_paths: list[str], batch_size: int = 8):
        results = []
        for audio_path in audio_paths:
            try:
                results.append(self.transcribe(audio_path, batch_size=batch_size))
            except Exception as exc:
                results.append(exc)
        return results
