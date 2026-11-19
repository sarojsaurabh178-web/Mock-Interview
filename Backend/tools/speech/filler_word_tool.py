from typing import Dict, Any
from services.speech_analysis_service import SpeechAnalysisService


def detect_filler_words(text: str) -> Dict[str, Any]:
    """
    detect_filler_words:
    Identify hesitation filler words (um, uh, like, actually, basically, you know) in speech transcript.
    """
    result = SpeechAnalysisService.detect_filler_words(text)
    return result.model_dump()


def synthesize_interviewer_speech(
    text: str,
    voice: str = "en-US-JennyNeural"
) -> Dict[str, Any]:
    """
    synthesize_interviewer_speech:
    Convert interviewer questions and prompts into voice audio bytes (base64 encoded).
    """
    result = SpeechAnalysisService.synthesize_interviewer_speech(text, voice)
    return result.model_dump()
