from typing import Dict, Any, Union, List
from services.resume_service import ResumeService
from schemas.interview import JDMatchResult


def match_resume_with_jd(
    resume_input: Union[Dict[str, Any], str],
    jd_input: Union[Dict[str, Any], str]
) -> Dict[str, Any]:
    """
    match_resume_with_jd:
    Compares candidate resume against target Job Description to identify
    skill alignment, missing technical competencies, and calculate match score.
    """
    resume_text = resume_input.get("raw_text", "") if isinstance(resume_input, dict) else str(resume_input)
    jd_text = jd_input.get("extracted_text", "") if isinstance(jd_input, dict) else str(jd_input)

    _, resume_skills = ResumeService._detect_skills(resume_text)
    _, jd_skills = ResumeService._detect_skills(jd_text)

    resume_set = {s.lower(): s for s in resume_skills}
    jd_set = {s.lower(): s for s in jd_skills}

    matching = [jd_set[k] for k in jd_set if k in resume_set]
    missing = [jd_set[k] for k in jd_set if k not in resume_set]

    total_jd = len(jd_set)
    if total_jd > 0:
        match_percentage = int((len(matching) / total_jd) * 100)
    else:
        match_percentage = 75 if resume_skills else 50

    if match_percentage >= 80:
        fit = "Strong Fit"
    elif match_percentage >= 50:
        fit = "Moderate Fit"
    else:
        fit = "Skill Gap Identified"

    recs: List[str] = []
    if missing:
        recs.append(f"Prepare questions addressing key missing requirements: {', '.join(missing[:4])}")
    if matching:
        recs.append(f"Probe depth of hands-on experience in matching strengths: {', '.join(matching[:4])}")
    recs.append("Assess architectural and behavioral trade-offs using STAR method.")

    summary = (
        f"Resume matches {len(matching)} of {total_jd} detected JD requirements ({match_percentage}%). "
        f"Candidate fit: {fit}."
    )

    result = JDMatchResult(
        match_score=min(match_percentage, 100),
        matching_skills=matching,
        missing_skills=missing,
        overall_fit=fit,
        summary=summary,
        recommendations=recs
    )

    return result.model_dump()
