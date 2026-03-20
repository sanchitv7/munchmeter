from groq import AsyncGroq
from app.config import settings


async def transcribe_audio(audio_bytes: bytes, filename: str = "audio.webm") -> str:
    """Transcribe audio bytes using Groq Whisper Large v3."""
    client = AsyncGroq(api_key=settings.groq_api_key)

    transcription = await client.audio.transcriptions.create(
        file=(filename, audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="text",
    )
    return transcription
