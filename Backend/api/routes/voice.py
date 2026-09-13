import os
import tempfile

from fastapi import (APIRouter,Depends,UploadFile,File)

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.session import get_db
from dependencies.auth import (get_current_user)
from database.models.user import User
from services.chat_service import (chat_service)
from services.stt_service import (speech_to_text)
from services.tts_service import (text_to_speech)

router = APIRouter(
    prefix="/voice",
    tags=["Voice"]
)


@router.post("")
async def voice_chat(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    # -------------------------
    # Save Upload Temporarily
    # -------------------------

    temp_audio = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )

    temp_audio.write(
        await file.read()
    )

    temp_audio.close()

    # -------------------------
    # Speech -> Text
    # -------------------------

    user_message = speech_to_text(
        temp_audio.name
    )

    # -------------------------
    # Agent
    # -------------------------

    result = chat_service(
        db=db,
        user_id=current_user.id,
        message=user_message
    )

    # -------------------------
    # Text -> Speech
    # -------------------------

    audio_path = text_to_speech(
        result.response
    )

    # -------------------------
    # Cleanup Input Audio
    # -------------------------

    os.remove(
        temp_audio.name
    )

    return FileResponse(
        path=audio_path,
        media_type="audio/mpeg",
        filename="response.mp3"
    )