from typing import Dict, Any, Optional
from services.interview_service import InterviewService


def get_current_question(session_id: str) -> Optional[Dict[str, Any]]:
    """
    get_current_question:
    Retrieve the active question for the given interview session.
    """
    q = InterviewService.get_current_question(session_id)
    return q.model_dump() if q else None


def generate_next_question(
    session_id: str,
    topic_hint: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    generate_next_question:
    Advance to the next question in the session or complete the round.
    """
    next_q = InterviewService.generate_next_question(session_id, topic_hint)
    return next_q.model_dump() if next_q else None
