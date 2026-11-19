from typing import Dict, Any, Optional, List, Union
from services.interview_service import InterviewService
from schemas.interview import InterviewPlan


def generate_interview_plan(
    target_role: str = "Fullstack Software Engineer",
    seniority: str = "Mid-Level",
    skills: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    generate_interview_plan:
    Create a complete interview structure with calibrated rounds, topics, and duration.
    """
    plan = InterviewService.generate_interview_plan(
        target_role=target_role,
        seniority=seniority,
        skills=skills
    )
    return plan.model_dump()


def start_interview(
    plan_or_role: Union[Dict[str, Any], str] = "Software Engineer"
) -> Dict[str, Any]:
    """
    start_interview:
    Initialize an interview session, prepare the sequence of questions, and set initial state.
    """
    if isinstance(plan_or_role, dict):
        plan_obj = InterviewPlan(**plan_or_role)
        session = InterviewService.start_interview(plan_or_role=plan_obj)
    else:
        session = InterviewService.start_interview(plan_or_role=str(plan_or_role))

    return session.model_dump()


def update_interview_progress(
    session_id: str,
    answer_record: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    update_interview_progress:
    Update session status, track completed questions, and record answers.
    """
    return InterviewService.update_interview_progress(session_id, answer_record)


def end_interview(session_id: str) -> Dict[str, Any]:
    """
    end_interview:
    Conclude an interview session, finalize timestamps, and generate session summary.
    """
    return InterviewService.end_interview(session_id)
