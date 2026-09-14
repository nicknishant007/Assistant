import os
import tempfile

from fastapi import (APIRouter,Depends,UploadFile,File)
import base64
from fastapi import Form
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
    conversation_id:str| None=Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):
    print("VOICE HIT")
    print(file.filename)

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
        conversation_id=conversation_id,
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

    with open(audio_path, "rb") as f:
        audio_base64 = base64.b64encode(
            f.read()
        ).decode()

    os.remove(audio_path)

    return {
        "conversation_id": result.conversation_id,
        "response": result.response,
        "user_message":user_message,
        "audio_base64": audio_base64,
    }