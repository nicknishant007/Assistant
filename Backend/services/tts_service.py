import asyncio
import tempfile

import edge_tts


async def _generate_audio(
    text: str,
    output_path: str
):

    communicate = edge_tts.Communicate(
        text=text,
        voice="en-US-AriaNeural"
    )

    await communicate.save(
        output_path
    )


def text_to_speech(
    text: str
) -> str:

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".mp3",
        delete=False
    )

    asyncio.run(
        _generate_audio(
            text,
            temp_file.name
        )
    )

    return temp_file.name