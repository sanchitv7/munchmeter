from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import TranscriptionResponse
from app.services.whisper import transcribe_audio

router = APIRouter()


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe(file: UploadFile = File(...)):
    """Transcribe an audio file using Groq Whisper Large v3."""
    if not file.content_type or not (
        file.content_type.startswith("audio/") or
        file.content_type in ("application/octet-stream", "video/webm")
    ):
        raise HTTPException(status_code=400, detail="File must be an audio file")

    audio_bytes = await file.read()
    if len(audio_bytes) == 0:
        raise HTTPException(status_code=400, detail="Audio file is empty")

    filename = file.filename or "audio.webm"
    text = await transcribe_audio(audio_bytes, filename)
    return TranscriptionResponse(text=text)
