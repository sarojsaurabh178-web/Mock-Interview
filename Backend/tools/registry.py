from typing import Callable, Dict, Any, List, Optional
from pydantic import BaseModel


class ToolDefinition(BaseModel):
    name: str
    description: str
    category: str
    parameters: Dict[str, Any]
    func: Optional[Callable] = None

    class Config:
        arbitrary_types_allowed = True


class ToolRegistry:
    """
    Central registry for all AI Interviewer tools.
    Enables agentic orchestration, LLM tool calling, and tool validation.
    """

    _registry: Dict[str, ToolDefinition] = {}

    @classmethod
    def register(
        cls,
        name: str,
        category: str,
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        func: Optional[Callable] = None
    ) -> None:
        cls._registry[name] = ToolDefinition(
            name=name,
            category=category,
            description=description,
            parameters=parameters or {},
            func=func
        )

    @classmethod
    def get(cls, name: str) -> Optional[ToolDefinition]:
        return cls._registry.get(name)

    @classmethod
    def list_tools(cls, category: Optional[str] = None) -> List[Dict[str, Any]]:
        tools = []
        for tool in cls._registry.values():
            if category is None or tool.category.lower() == category.lower():
                tools.append({
                    "name": tool.name,
                    "category": tool.category,
                    "description": tool.description,
                    "parameters": tool.parameters
                })
        return tools

    @classmethod
    def execute(cls, name: str, **kwargs) -> Any:
        tool = cls.get(name)
        if not tool or not tool.func:
            raise ValueError(f"Tool '{name}' is not registered or has no executable function.")
        return tool.func(**kwargs)


# ----------------------------------------------------
# 1. Candidate & Document Analysis Tools
# ----------------------------------------------------
from tools.candidate.resume_tools import (
    parse_resume,
    analyze_resume,
    extract_candidate_skills,
    extract_candidate_experience,
    extract_candidate_projects,
    extract_candidate_achievements,
)
from tools.candidate.jd_tools import match_resume_with_jd

ToolRegistry.register(
    name="parse_resume",
    category="Candidate & Document Analysis",
    description="Extract structured text, contact info, and basic skills from candidate resume PDF/DOCX/TXT file.",
    parameters={
        "type": "object",
        "properties": {
            "filename": {"type": "string", "description": "Name of the resume file"},
            "content": {"type": "string", "description": "Raw bytes of the document"}
        },
        "required": ["filename", "content"]
    },
    func=parse_resume
)

ToolRegistry.register(
    name="analyze_resume",
    category="Candidate & Document Analysis",
    description="Analyze candidate skills, experience, education, projects, achievements, and recommend interview focus areas.",
    parameters={
        "type": "object",
        "properties": {
            "resume_input": {"type": "string", "description": "Raw resume text, bytes, or parsed resume dictionary"},
            "filename": {"type": "string", "description": "Optional filename"}
        },
        "required": ["resume_input"]
    },
    func=analyze_resume
)

ToolRegistry.register(
    name="match_resume_with_jd",
    category="Candidate & Document Analysis",
    description="Compare candidate resume against Job Description to calculate match score and identify skill gaps.",
    parameters={
        "type": "object",
        "properties": {
            "resume_input": {"type": "string", "description": "Resume text or parsed dictionary"},
            "jd_input": {"type": "string", "description": "Job description text or parsed dictionary"}
        },
        "required": ["resume_input", "jd_input"]
    },
    func=match_resume_with_jd
)

ToolRegistry.register(
    name="extract_candidate_skills",
    category="Candidate & Document Analysis",
    description="Extract technical and soft skills grouped by engineering domains.",
    parameters={"type": "object", "properties": {"text_or_resume": {"type": "string"}}, "required": ["text_or_resume"]},
    func=extract_candidate_skills
)

ToolRegistry.register(
    name="extract_candidate_experience",
    category="Candidate & Document Analysis",
    description="Extract work experience, estimated years in field, and seniority level.",
    parameters={"type": "object", "properties": {"text_or_resume": {"type": "string"}}, "required": ["text_or_resume"]},
    func=extract_candidate_experience
)

ToolRegistry.register(
    name="extract_candidate_projects",
    category="Candidate & Document Analysis",
    description="Extract project details, technologies used, and architectural highlights.",
    parameters={"type": "object", "properties": {"text_or_resume": {"type": "string"}}, "required": ["text_or_resume"]},
    func=extract_candidate_projects
)

ToolRegistry.register(
    name="extract_candidate_achievements",
    category="Candidate & Document Analysis",
    description="Extract certifications and competitive achievements.",
    parameters={"type": "object", "properties": {"text_or_resume": {"type": "string"}}, "required": ["text_or_resume"]},
    func=extract_candidate_achievements
)


# ----------------------------------------------------
# 2. Interview Planning Tools
# ----------------------------------------------------
from tools.interview.session_tools import (
    generate_interview_plan,
    start_interview,
    update_interview_progress,
    end_interview,
)

ToolRegistry.register(
    name="generate_interview_plan",
    category="Interview Planning",
    description="Create the complete interview plan defining technical and behavioral rounds, duration, and topics.",
    parameters={
        "type": "object",
        "properties": {
            "target_role": {"type": "string", "description": "Role being interviewed for"},
            "seniority": {"type": "string", "description": "Target seniority level"},
            "skills": {"type": "array", "items": {"type": "string"}, "description": "Key target technical skills"}
        }
    },
    func=generate_interview_plan
)


# ----------------------------------------------------
# 3. Interview Management Tools
# ----------------------------------------------------
from tools.interview.question_tools import (
    get_current_question,
    generate_next_question,
)

ToolRegistry.register(
    name="start_interview",
    category="Interview Management",
    description="Start an interview session and initialize question sequences.",
    parameters={
        "type": "object",
        "properties": {
            "plan_or_role": {"type": "string", "description": "Interview plan dictionary or role title"}
        }
    },
    func=start_interview
)

ToolRegistry.register(
    name="get_current_question",
    category="Interview Management",
    description="Retrieve the current active interview question for a session.",
    parameters={
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "Unique session ID"}
        },
        "required": ["session_id"]
    },
    func=get_current_question
)

ToolRegistry.register(
    name="generate_next_question",
    category="Interview Management",
    description="Advance the session and generate the next interview question.",
    parameters={
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "Unique session ID"},
            "topic_hint": {"type": "string", "description": "Optional topic override"}
        },
        "required": ["session_id"]
    },
    func=generate_next_question
)

ToolRegistry.register(
    name="update_interview_progress",
    category="Interview Management",
    description="Update session progress, completed questions, and answers history.",
    parameters={
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "Unique session ID"},
            "answer_record": {"type": "object", "description": "Answer evaluation record"}
        },
        "required": ["session_id"]
    },
    func=update_interview_progress
)

ToolRegistry.register(
    name="end_interview",
    category="Interview Management",
    description="Conclude the interview session and calculate final performance summary.",
    parameters={
        "type": "object",
        "properties": {
            "session_id": {"type": "string", "description": "Unique session ID"}
        },
        "required": ["session_id"]
    },
    func=end_interview
)


# ----------------------------------------------------
# 4. Answer Evaluation Tools
# ----------------------------------------------------
from tools.interview.answer_tools import evaluate_candidate_answer
from tools.interview.followup_tools import generate_followup_question

ToolRegistry.register(
    name="evaluate_candidate_answer",
    category="Answer Evaluation",
    description="Evaluate candidate answer against STAR rubric, score relevance and completeness, and provide constructive feedback.",
    parameters={
        "type": "object",
        "properties": {
            "question_id": {"type": "string", "description": "Question ID"},
            "question_text": {"type": "string", "description": "Text of the interview question"},
            "answer_text": {"type": "string", "description": "Candidate's response"},
            "expected_points": {"type": "array", "items": {"type": "string"}, "description": "Expected key concepts"}
        },
        "required": ["question_id", "question_text", "answer_text"]
    },
    func=evaluate_candidate_answer
)

ToolRegistry.register(
    name="generate_followup_question",
    category="Answer Evaluation",
    description="Generate a targeted follow-up question probing technical trade-offs, architecture, or quantifiable results.",
    parameters={
        "type": "object",
        "properties": {
            "question_id": {"type": "string", "description": "Question ID"},
            "question_text": {"type": "string", "description": "Original question text"},
            "answer_text": {"type": "string", "description": "Candidate answer text"},
            "evaluation": {"type": "object", "description": "Optional previous evaluation dictionary"}
        },
        "required": ["question_id", "question_text", "answer_text"]
    },
    func=generate_followup_question
)


# ----------------------------------------------------
# 5. Speech Analysis Tools
# ----------------------------------------------------
from tools.speech.transcription_tool import transcribe_candidate_audio
from tools.speech.speaking_pace_tool import analyze_speaking_pace
from tools.speech.pause_analysis_tool import analyze_speech_pauses, analyze_audio_quality
from tools.speech.filler_word_tool import detect_filler_words, synthesize_interviewer_speech

ToolRegistry.register(
    name="transcribe_candidate_audio",
    category="Speech Analysis",
    description="Convert candidate speech audio into text with confidence score.",
    parameters={
        "type": "object",
        "properties": {
            "audio_input": {"type": "string", "description": "Audio file path or bytes"},
            "filename": {"type": "string", "description": "Audio filename"},
            "language": {"type": "string", "description": "Spoken language code (e.g. 'en')"}
        },
        "required": ["audio_input"]
    },
    func=transcribe_candidate_audio
)

ToolRegistry.register(
    name="analyze_speaking_pace",
    category="Speech Analysis",
    description="Calculate words per minute (WPM) and classify speaking cadence.",
    parameters={
        "type": "object",
        "properties": {
            "word_count": {"type": "integer", "description": "Number of words spoken"},
            "duration_seconds": {"type": "number", "description": "Duration of speech in seconds"},
            "text": {"type": "string", "description": "Optional speech transcript"}
        }
    },
    func=analyze_speaking_pace
)

ToolRegistry.register(
    name="analyze_speech_pauses",
    category="Speech Analysis",
    description="Measure silence intervals, hesitation pauses, and pacing continuity.",
    parameters={
        "type": "object",
        "properties": {
            "audio_input": {"type": "string", "description": "Audio file path or bytes"},
            "silence_threshold_db": {"type": "number", "description": "Silence threshold in decibels"}
        },
        "required": ["audio_input"]
    },
    func=analyze_speech_pauses
)

ToolRegistry.register(
    name="detect_filler_words",
    category="Speech Analysis",
    description="Count and identify filler words (um, uh, like, actually, basically, you know) and calculate frequency percentage.",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Candidate speech transcript"}
        },
        "required": ["text"]
    },
    func=detect_filler_words
)

ToolRegistry.register(
    name="analyze_audio_quality",
    category="Speech Analysis",
    description="Detect microphone clipping, signal-to-noise ratio (SNR), and room noise level.",
    parameters={
        "type": "object",
        "properties": {
            "audio_input": {"type": "string", "description": "Audio file path or bytes"}
        },
        "required": ["audio_input"]
    },
    func=analyze_audio_quality
)

ToolRegistry.register(
    name="synthesize_interviewer_speech",
    category="Speech Analysis",
    description="Convert interviewer questions and prompts into voice audio bytes (base64).",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to convert to voice"},
            "voice": {"type": "string", "description": "Voice identifier (e.g. 'en-US-JennyNeural')"}
        },
        "required": ["text"]
    },
    func=synthesize_interviewer_speech
)

