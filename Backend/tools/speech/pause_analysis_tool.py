from typing import Dict, Any, Union
from pathlib import Path
from services.speech_analysis_service import SpeechAnalysisService


def analyze_speech_pauses(
    audio_input: Union[bytes, str],
    silence_threshold_db: float = -32.0,
    min_pause_duration_ms: float = 350.0
) -> Dict[str, Any]:
    """
    analyze_speech_pauses:
    Measure silence intervals, hesitation pauses, and pacing continuity.
    """
    if isinstance(audio_input, str):
        path = Path(audio_input)
        if path.is_file():
            content = path.read_bytes()
        else:
            raise FileNotFoundError(f"Audio file not found: {audio_input}")
    else:
        content = audio_input

    result = SpeechAnalysisService.analyze_speech_pauses(
        audio_content=content,
        silence_threshold_db=silence_threshold_db,
        min_pause_duration_ms=min_pause_duration_ms
    )
    return result.model_dump()


def analyze_audio_quality(audio_input: Union[bytes, str]) -> Dict[str, Any]:
    """
    analyze_audio_quality:
    Detect microphone clipping, signal-to-noise ratio, and room noise floor.
    """
    if isinstance(audio_input, str):
        path = Path(audio_input)
        if path.is_file():
            content = path.read_bytes()
        else:
            raise FileNotFoundError(f"Audio file not found: {audio_input}")
    else:
        content = audio_input

    result = SpeechAnalysisService.analyze_audio_quality(content)
    return result.model_dump()
