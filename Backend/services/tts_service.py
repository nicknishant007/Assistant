import tempfile
import edge_tts


async def text_to_speech(text: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    )

    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-AriaNeural"
    )

    await communicate.save(
        temp_file.name
    )

    return temp_file.name