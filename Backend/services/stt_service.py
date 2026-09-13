from faster_whisper import WhisperModel

model = WhisperModel(
    "base",
    device="cpu",
    compute_type="int8"
)


def speech_to_text(audio_path: str) -> str:

    segments, _ = model.transcribe(
        audio_path
    )

    text = " ".join(
        segment.text.strip()
        for segment in segments
    )

    return text.strip()