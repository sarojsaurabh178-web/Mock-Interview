from typing import Dict, Any, Optional, List
from services.evaluation_service import EvaluationService


def evaluate_candidate_answer(
    question_id: str,
    question_text: str,
    answer_text: str,
    expected_points: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    evaluate_candidate_answer:
    Evaluate candidate response using STAR criteria, calculate relevance and completeness,
    and generate constructive feedback and follow-up flags.
    """
    eval_result = EvaluationService.evaluate_candidate_answer(
        question_id=question_id,
        question_text=question_text,
        answer_text=answer_text,
        expected_points=expected_points
    )
    return eval_result.model_dump()
