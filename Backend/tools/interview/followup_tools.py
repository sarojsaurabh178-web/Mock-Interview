from typing import Dict, Any, Optional
from services.evaluation_service import EvaluationService
from schemas.interview import AnswerEvaluation


def generate_followup_question(
    question_id: str,
    question_text: str,
    answer_text: str,
    evaluation: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    generate_followup_question:
    Generate an adaptive follow-up question probing technical depth, trade-offs, or quantifiable metrics.
    """
    eval_obj = AnswerEvaluation(**evaluation) if evaluation else None
    fup = EvaluationService.generate_followup_question(
        question_id=question_id,
        question_text=question_text,
        answer_text=answer_text,
        evaluation=eval_obj
    )
    return fup.model_dump()
