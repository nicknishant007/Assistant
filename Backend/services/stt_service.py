from faster_whisper import WhisperModel

_model = None


def get_model():
    global _model
    if _model is None:
        _model = WhisperModel(
            "base",
            device="cpu",
            compute_type="int8"
        )
    return _model


def speech_to_text(audio_path: str) -> str:

    model = get_model()

    segments, _ = model.transcribe(
        audio_path
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
    )

    return text.strip()