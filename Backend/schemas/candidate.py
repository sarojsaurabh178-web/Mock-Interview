from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ContactInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None


class WorkExperience(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    duration: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    is_current: bool = False
    highlights: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class Education(BaseModel):
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    institution: Optional[str] = None
    year: Optional[str] = None


class ProjectDetail(BaseModel):
    name: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)


class AchievementDetail(BaseModel):
    title: str
    issuer_or_detail: Optional[str] = None
    year: Optional[str] = None


class ExperienceAnalysis(BaseModel):
    total_years_estimated: float = 0.0
    seniority_level: str = "Entry-Level"
    items: List[WorkExperience] = Field(default_factory=list)
    quantifiable_metrics_count: int = 0


class SkillsAnalysis(BaseModel):
    total_skills_count: int = 0
    primary_domain: str = "General Engineering"
    top_skills: List[str] = Field(default_factory=list)
    categorized: Dict[str, List[str]] = Field(default_factory=dict)


class EducationAnalysis(BaseModel):
    items: List[Education] = Field(default_factory=list)
    highest_degree: Optional[str] = None


class ResumeAnalysisResult(BaseModel):
    resume_id: str
    candidate_name: Optional[str] = None
    executive_summary: str
    skills_analysis: SkillsAnalysis
    experience_analysis: ExperienceAnalysis
    education_analysis: EducationAnalysis
    projects: List[ProjectDetail] = Field(default_factory=list)
    achievements: List[AchievementDetail] = Field(default_factory=list)
    completeness_score: int = Field(ge=0, le=100)
    recommended_interview_focus: List[str] = Field(default_factory=list)


class ParsedResume(BaseModel):
    resume_id: str
    filename: str
    file_size_bytes: int
    page_count: int
    word_count: int
    contact_info: ContactInfo
    detected_skills: List[str] = Field(default_factory=list)
    categorized_skills: Dict[str, List[str]] = Field(default_factory=dict)
    sections_detected: List[str] = Field(default_factory=list)
    preview_text: str
    raw_text: str


class ResumeUploadResponse(BaseModel):
    status: str
    message: str
    data: ParsedResume


class ResumeAnalysisResponse(BaseModel):
    status: str
    message: str
    data: ResumeAnalysisResult
