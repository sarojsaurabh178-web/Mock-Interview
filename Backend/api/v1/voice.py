from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from services.speech_analysis_service import SpeechAnalysisService
from schemas.speech import (
    TranscriptionResult,
    SpeakingPaceResult,
    PauseAnalysisResult,
    FillerWordDetectionResult,
    AudioQualityResult,
    SynthesizeSpeechResult,
)

router = APIRouter(prefix="/voice", tags=["Voice & Speech Analysis"])


class PaceAnalysisRequest(BaseModel):
    word_count: Optional[int] = None
    duration_seconds: float = 60.0
    text: Optional[str] = None


class FillerDetectionRequest(BaseModel):
    text: str


class SynthesizeRequest(BaseModel):
    text: str
    voice: str = "en-US-JennyNeural"


MAX_AUDIO_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB Groq Whisper maximum limit


@router.post("/transcribe", response_model=TranscriptionResult)
async def transcribe_endpoint(file: UploadFile = File(...), language: str = Form("en")):
    """
    POST /api/v1/voice/transcribe
    Upload candidate audio file and convert speech into text using Groq Whisper.
    """
    filename = file.filename or "candidate_voice.webm"
    content_type = file.content_type or "audio/webm"

    print("\n" + "=" * 65)
    print("🎧 [AUDIO INGEST] Inbound candidate speech upload")
    print(f"📁 Filename:     {filename}")
    print(f"📦 Content-Type: {content_type}")

    content = await file.read()
    byte_size = len(content)
    print(f"📊 Payload Size: {byte_size:,} bytes ({round(byte_size / 1024, 2)} KB)")

    if byte_size == 0:
        print("❌ [AUDIO ERROR] Received empty 0-byte audio file.")
        print("=" * 65 + "\n")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded audio file is empty (0 bytes). Please ensure microphone permissions are granted and record again."
        )

    if byte_size > MAX_AUDIO_SIZE_BYTES:
        print(f"❌ [AUDIO ERROR] Audio exceeds 25MB: {byte_size:,} bytes.")
        print("=" * 65 + "\n")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Audio file exceeds the 25MB limit supported by Groq Whisper."
        )

    print("=" * 65)
    return SpeechAnalysisService.transcribe_candidate_audio(
        audio_content=content,
        filename=filename,
        language=language
    )


@router.post("/analyze-pace", response_model=SpeakingPaceResult)
def pace_endpoint(req: PaceAnalysisRequest):
    """
    POST /api/v1/voice/analyze-pace
    Calculate words per minute (WPM) and pacing feedback.
    """
    wc = req.word_count or (len(req.text.split()) if req.text else 0)
    return SpeechAnalysisService.analyze_speaking_pace(wc, req.duration_seconds, req.text)


@router.post("/analyze-pauses", response_model=PauseAnalysisResult)
async def pauses_endpoint(file: UploadFile = File(...)):
    """
    POST /api/v1/voice/analyze-pauses
    Analyze speech pauses, hesitations, and silence percentage.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Audio file is empty.")
    return SpeechAnalysisService.analyze_speech_pauses(content)


@router.post("/detect-fillers", response_model=FillerWordDetectionResult)
def fillers_endpoint(req: FillerDetectionRequest):
    """
    POST /api/v1/voice/detect-fillers
    Identify filler words (um, uh, like, actually) and calculate frequency percentage.
    """
    return SpeechAnalysisService.detect_filler_words(req.text)


@router.post("/audio-quality", response_model=AudioQualityResult)
async def audio_quality_endpoint(file: UploadFile = File(...)):
    """
    POST /api/v1/voice/audio-quality
    Inspect signal clipping, SNR, and background noise level.
    """
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Audio file is empty.")
    return SpeechAnalysisService.analyze_audio_quality(content)


@router.post("/synthesize", response_model=SynthesizeSpeechResult)
def synthesize_endpoint(req: SynthesizeRequest):
    """
    POST /api/v1/voice/synthesize
    Convert interviewer questions into voice audio (base64 string).
    """
    return SpeechAnalysisService.synthesize_interviewer_speech(req.text, req.voice)
