from pathlib import Path
from typing import Dict, Any, List, Union
from services.resume_service import ResumeService
from schemas.candidate import ParsedResume


def parse_resume(filename: str, content: bytes) -> Dict[str, Any]:
    """
    parse_resume:
    Extract structured information from PDF/DOCX/TXT file bytes.
    """
    parsed = ResumeService.parse_resume(filename, content)
    return parsed.model_dump()


def parse_resume_from_disk(file_path: str) -> Dict[str, Any]:
    """
    Helper tool to parse a resume from a local file path.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Resume file not found at: {file_path}")

    content = path.read_bytes()
    return parse_resume(path.name, content)


def analyze_resume(resume_input: Union[Dict[str, Any], str, bytes], filename: str = "resume.txt") -> Dict[str, Any]:
    """
    analyze_resume:
    Analyze candidate skills, experience, education, projects, achievements,
    calculating estimated years, seniority level, and recommended interview focus.
    """
    if isinstance(resume_input, bytes):
        parsed = ResumeService.parse_resume(filename, resume_input)
        analysis = ResumeService.analyze_resume(parsed)
    elif isinstance(resume_input, dict) and "raw_text" in resume_input:
        parsed = ParsedResume(**resume_input)
        analysis = ResumeService.analyze_resume(parsed)
    elif isinstance(resume_input, str):
        analysis = ResumeService.analyze_resume(resume_input, filename=filename)
    else:
        raise ValueError("Invalid resume input format. Must be resume text, bytes, or parsed resume dict.")

    return analysis.model_dump()


def extract_candidate_skills(text_or_resume: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    extract_candidate_skills:
    Extract and categorize technical and soft skills from candidate resume.
    """
    text = text_or_resume["raw_text"] if isinstance(text_or_resume, dict) and "raw_text" in text_or_resume else str(text_or_resume)
    skills = ResumeService.extract_candidate_skills(text)
    return skills.model_dump()


def extract_candidate_experience(text_or_resume: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    extract_candidate_experience:
    Extract work experience, employment intervals, and infer seniority level.
    """
    text = text_or_resume["raw_text"] if isinstance(text_or_resume, dict) and "raw_text" in text_or_resume else str(text_or_resume)
    exp = ResumeService.extract_candidate_experience(text)
    return exp.model_dump()


def extract_candidate_projects(text_or_resume: Union[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    extract_candidate_projects:
    Extract project details, architectures, and technologies from resume.
    """
    text = text_or_resume["raw_text"] if isinstance(text_or_resume, dict) and "raw_text" in text_or_resume else str(text_or_resume)
    skills = ResumeService.extract_candidate_skills(text)
    projects = ResumeService.extract_candidate_projects(text, skills.top_skills)
    return [p.model_dump() for p in projects]


def extract_candidate_achievements(text_or_resume: Union[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    extract_candidate_achievements:
    Extract certifications, honors, and competitive achievements from resume.
    """
    text = text_or_resume["raw_text"] if isinstance(text_or_resume, dict) and "raw_text" in text_or_resume else str(text_or_resume)
    achievements = ResumeService.extract_candidate_achievements(text)
    return [a.model_dump() for a in achievements]
