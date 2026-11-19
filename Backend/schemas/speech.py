from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class TranscriptionResult(BaseModel):
    text: str
    transcript: Optional[str] = None
    language: str = "en"
    duration_seconds: float
    duration: Optional[float] = None
    word_count: int
    confidence: float = Field(default=0.92, ge=0.0, le=1.0)


class SpeakingPaceResult(BaseModel):
    words_per_minute: float
    word_count: int
    duration_seconds: float
    pace_category: str  # "Too Slow", "Optimal", "Fast", "Too Fast"
    feedback: str


class PauseAnalysisResult(BaseModel):
    total_pauses_count: int
    average_pause_duration_seconds: float
    longest_pause_seconds: float
    silence_percentage: float
    pause_frequency_per_minute: float
    assessment: str


class FillerWordDetectionResult(BaseModel):
    total_filler_count: int
    filler_frequency_percentage: float
    filler_breakdown: Dict[str, int] = Field(default_factory=dict)
    severity: str  # "Clean", "Moderate", "High"
    recommendations: List[str] = Field(default_factory=list)


class AudioQualityResult(BaseModel):
    snr_db: float
    is_clipping: bool
    volume_level_db: float
    background_noise_level: str  # "Low / Clean", "Moderate", "High"
    quality_score: int = Field(ge=0, le=100)
    issues_detected: List[str] = Field(default_factory=list)


class SynthesizeSpeechResult(BaseModel):
    audio_base64: str
    audio_format: str = "mp3"
    duration_seconds_estimated: float
    voice_used: str
    character_count: int
