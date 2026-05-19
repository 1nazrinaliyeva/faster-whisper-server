import os

from faster_whisper import WhisperModel

try:
    from faster_whisper import BatchedInferencePipeline
except ImportError:
    BatchedInferencePipeline = None


class WhisperEngine:
    def __init__(
        self,
        model_size="small",
        device="cpu",
        compute_type="int8",
        language=None,
        task="transcribe",
        beam_size=5,
        batch_size=8,
        vad_filter=True,
        initial_prompt=None,
    ):
        self.model_name_or_path = os.path.expanduser(model_size)
        self.model_is_local = os.path.isdir(self.model_name_or_path)
        _validate_model_name_or_path(self.model_name_or_path)
        self.language = language
        self.task = task
        self.beam_size = beam_size
        self.batch_size = batch_size
        self.vad_filter = vad_filter
        self.initial_prompt = initial_prompt
        self.model = WhisperModel(
            self.model_name_or_path,
            device=device,
            compute_type=compute_type
        )
        self.pipeline = (
            BatchedInferencePipeline(model=self.model)
            if BatchedInferencePipeline is not None
            else self.model
        )
        self.uses_batched_pipeline = BatchedInferencePipeline is not None

    def transcribe(
        self,
        audio_path: str,
        batch_size: int | None = None,
        language: str | None = None,
        use_language_override: bool = False,
    ):
        effective_batch_size = batch_size or self.batch_size
        effective_language = language if use_language_override else self.language
        options = {
            "language": effective_language,
            "task": self.task,
            "beam_size": self.beam_size,
            "vad_filter": self.vad_filter,
            "initial_prompt": self.initial_prompt,
        }
        if self.uses_batched_pipeline:
            segments, info = self.pipeline.transcribe(
                audio_path,
                batch_size=effective_batch_size,
                **options,
            )
        else:
            segments, info = self.pipeline.transcribe(audio_path, **options)
        text = " ".join(segment.text for segment in segments)

        return {
            "text": text,
            "language": info.language,
            "duration": info.duration
        }

    def transcribe_batch(
        self,
        audio_paths: list[str],
        batch_size: int | None = None,
        languages: list[str | None] | None = None,
        language_overrides: list[bool] | None = None,
    ):
        results = []
        languages = languages or [None] * len(audio_paths)
        language_overrides = language_overrides or [False] * len(audio_paths)
        for audio_path, language, use_language_override in zip(
            audio_paths,
            languages,
            language_overrides,
        ):
            try:
                results.append(
                    self.transcribe(
                        audio_path,
                        batch_size=batch_size,
                        language=language,
                        use_language_override=use_language_override,
                    )
                )
            except Exception as exc:
                results.append(exc)
        return results


def _validate_model_name_or_path(model_name_or_path: str) -> None:
    looks_like_path = (
        model_name_or_path.startswith("/")
        or model_name_or_path.startswith("./")
        or model_name_or_path.startswith("../")
        or model_name_or_path.startswith("~")
    )
    if looks_like_path and not os.path.isdir(model_name_or_path):
        raise FileNotFoundError(
            "WHISPER_MODEL looks like a local path, but the directory does not "
            f"exist: {model_name_or_path}"
        )
