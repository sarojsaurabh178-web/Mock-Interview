from typing import Dict, Any, Optional
from services.speech_analysis_service import SpeechAnalysisService


def analyze_speaking_pace(
    word_count: int = 0,
    duration_seconds: float = 60.0,
    text: Optional[str] = None
) -> Dict[str, Any]:
    """
    analyze_speaking_pace:
    Calculate candidate words per minute (WPM) and classify into pacing tiers.
    """
    result = SpeechAnalysisService.analyze_speaking_pace(
        word_count=word_count,
        duration_seconds=duration_seconds,
        text=text
    )
    return result.model_dump()
