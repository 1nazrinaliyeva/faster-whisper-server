from faster_whisper import BatchedInferencePipeline, WhisperModel


class WhisperEngine:
    def __init__(self, model_size="small", device="cpu", compute_type="int8"):
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        self.pipeline = BatchedInferencePipeline(model=self.model)

    def transcribe(self, audio_path: str, batch_size: int = 8):
        segments, info = self.pipeline.transcribe(
            audio_path,
            beam_size=5,
            batch_size=batch_size,
        )
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
