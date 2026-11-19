from typing import Dict, Any, Union
from pathlib import Path
from services.speech_analysis_service import SpeechAnalysisService


def transcribe_candidate_audio(
    audio_input: Union[bytes, str],
    filename: str = "audio.wav",
    language: str = "en"
) -> Dict[str, Any]:
    """
    transcribe_candidate_audio:
    Convert candidate spoken audio into structured text with duration and confidence metrics.
    """
    if isinstance(audio_input, str):
        path = Path(audio_input)
        if path.is_file():
            content = path.read_bytes()
            filename = path.name
        else:
            raise FileNotFoundError(f"Audio file not found: {audio_input}")
    else:
        content = audio_input

    result = SpeechAnalysisService.transcribe_candidate_audio(
        audio_content=content,
        filename=filename,
        language=language
    )
    return result.model_dump()
