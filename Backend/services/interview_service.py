import uuid
import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union
from schemas.interview import (
    InterviewPlan,
    InterviewRound,
    InterviewQuestion,
    InterviewSession,
)
from ai.llm.llm_manager import LLMManager


class InterviewService:
    """
    Core engine managing interview lifecycle: planning, starting, progression,
    adaptive question sequencing, and session completion.
    """

    _sessions: Dict[str, InterviewSession] = {}

    QUESTION_TEMPLATES = [
        {
            "round": "Technical Core",
            "topic": "Architecture & Data Flow",
            "question": "Can you walk me through the architecture of a complex application you designed or contributed to? How did data flow between the frontend and backend?",
            "intent": "Assess system comprehension, component modularity, and API design.",
            "expected": ["Data pipeline / API contract", "State management", "Error handling and caching"]
        },
        {
            "round": "Technical Deep-Dive",
            "topic": "Performance & Scalability",
            "question": "Describe a specific performance bottleneck or latency issue you encountered. What tools did you use to diagnose it, and how did you resolve it?",
            "intent": "Evaluate diagnostic ability, profiling, and optimization techniques.",
            "expected": ["Profiling tool identification", "Root cause explanation", "Measurable performance gain"]
        },
        {
            "round": "Behavioral",
            "topic": "Conflict Resolution & Collaboration",
            "question": "Tell me about a time you had a technical disagreement with a team member or stakeholder. How did you handle the situation and what was the outcome?",
            "intent": "Evaluate STAR framework delivery, empathy, compromise, and professional maturity.",
            "expected": ["Situation & Task context", "Constructive Action taken", "Measurable or positive Result"]
        },
        {
            "round": "System Design",
            "topic": "Resilience & Error Handling",
            "question": "How do you handle graceful degradation and failure modes when an external third-party service or database fails in your system?",
            "intent": "Check fault tolerance, circuit breakers, retry backoff, and fallback UI.",
            "expected": ["Circuit breaker / retry strategy", "Asynchronous queues / fallbacks", "User experience degradation"]
        },
        {
            "round": "Leadership & Process",
            "topic": "Code Quality & Mentorship",
            "question": "How do you maintain high code quality and test coverage in your team while balancing tight deadlines?",
            "intent": "Assess engineering standards, code reviews, CI/CD practices, and prioritization.",
            "expected": ["Automated test suites / CI/CD", "Thorough code reviews", "Pragmatic technical debt management"]
        }
    ]

    @classmethod
    def generate_interview_plan(
        cls,
        target_role: str = "Fullstack Software Engineer",
        seniority: str = "Mid-Level",
        skills: Optional[List[str]] = None
    ) -> InterviewPlan:
        """
        Creates a structured interview plan with calibrated rounds, duration, and question allocation.
        """
        plan_id = f"plan_{uuid.uuid4().hex[:10]}"
        skills = skills or ["React", "FastAPI", "System Design", "Databases"]

        rounds = [
            InterviewRound(
                round_name="Technical Core",
                topics=skills[:2],
                question_count=2,
                estimated_minutes=10
            ),
            InterviewRound(
                round_name="Behavioral & Problem Solving",
                topics=["STAR Method", "Cross-Functional Collaboration"],
                question_count=1,
                estimated_minutes=5
            ),
            InterviewRound(
                round_name="System Design & Scalability",
                topics=["Architecture", "Performance", "Security"],
                question_count=2,
                estimated_minutes=10
            )
        ]

        total_questions = sum(r.question_count for r in rounds)
        total_duration = sum(r.estimated_minutes for r in rounds)

        return InterviewPlan(
            plan_id=plan_id,
            target_role=target_role,
            difficulty_level=seniority,
            rounds=rounds,
            total_questions=total_questions,
            total_duration_minutes=total_duration
        )

    @classmethod
    def start_interview(
        cls,
        plan_or_role: Union[InterviewPlan, str] = "Software Engineer",
        questions: Optional[List[InterviewQuestion]] = None
    ) -> InterviewSession:
        """
        Initializes and registers a new active interview session.
        """
        session_id = f"session_{uuid.uuid4().hex[:12]}"

        if isinstance(plan_or_role, InterviewPlan):
            plan = plan_or_role
        else:
            plan = cls.generate_interview_plan(target_role=str(plan_or_role))

        # Generate custom tailored questions via LLM if not provided
        if not questions:
            questions = []
            prompt = f"""Generate 5 realistic, progressive technical interview questions for the following role:
Role: {plan.target_role}
Seniority: {plan.difficulty_level}

Requirements:
- 1st question: Icebreaker & architecture overview.
- 2nd question: Deep technical problem solving & performance.
- 3rd question: Behavioral / STAR methodology (conflict, ownership, or leadership).
- 4th question: System design / scalability or edge cases.
- 5th question: Code quality, testing, or best practices.

Return ONLY a valid JSON list of 5 objects matching this schema:
[
  {{
    "round": "Technical Core",
    "topic": "<Specific Topic>",
    "question": "<The question text to ask the candidate>",
    "intent": "<What this question assesses>",
    "expected": ["<key expected point 1>", "<key expected point 2>"]
  }}
]"""
            raw_llm = LLMManager.call_llm(
                prompt=prompt,
                system_instruction="You are a Principal Engineer and veteran technical interviewer at a top tech company. Return only valid JSON.",
                temperature=0.3,
                max_tokens=1000,
                context_name="InterviewQuestionGeneration"
            )

            parsed_list = None
            if raw_llm:
                try:
                    clean = raw_llm.strip()
                    if clean.startswith("```"):
                        clean = re.sub(r"^```(?:json)?\s*", "", clean)
                        clean = re.sub(r"\s*```$", "", clean)
                    parsed_list = json.loads(clean)
                except Exception as e:
                    print(f"[InterviewService] Question JSON parse warning: {e}")

            template_bank = parsed_list if (parsed_list and isinstance(parsed_list, list)) else cls.QUESTION_TEMPLATES

            for idx, tmpl in enumerate(template_bank[:5], start=1):
                questions.append(
                    InterviewQuestion(
                        question_id=f"q_{uuid.uuid4().hex[:8]}",
                        question_number=idx,
                        round_name=tmpl.get("round", "Technical Core"),
                        topic=tmpl.get("topic", "Engineering Fundamentals"),
                        question_text=tmpl.get("question", "Can you describe a challenging project you contributed to?"),
                        intent=tmpl.get("intent", "Evaluate problem-solving and architectural clarity."),
                        difficulty=plan.difficulty_level,
                        time_limit_minutes=3,
                        expected_points=tmpl.get("expected", ["System design", "Performance"])
                    )
                )

        started_at = datetime.now(timezone.utc).isoformat()

        session = InterviewSession(
            session_id=session_id,
            target_role=plan.target_role,
            status="IN_PROGRESS",
            current_question_index=0,
            plan=plan,
            questions=questions,
            history=[],
            progress_percentage=0,
            started_at=started_at
        )

        cls._sessions[session_id] = session
        return session

    @classmethod
    def get_session(cls, session_id: str) -> InterviewSession:
        """Retrieve an active or completed session by ID."""
        session = cls._sessions.get(session_id)
        if not session:
            raise KeyError(f"Interview session '{session_id}' not found.")
        return session

    @classmethod
    def get_current_question(cls, session_id: str) -> Optional[InterviewQuestion]:
        """Retrieve the currently active interview question."""
        session = cls.get_session(session_id)
        if session.current_question_index < len(session.questions):
            return session.questions[session.current_question_index]
        return None

    @classmethod
    def generate_next_question(
        cls,
        session_id: str,
        topic_hint: Optional[str] = None
    ) -> Optional[InterviewQuestion]:
        """
        Advances the session to the next question or returns None if interview complete.
        """
        session = cls.get_session(session_id)
        next_index = session.current_question_index + 1

        if next_index < len(session.questions):
            session.current_question_index = next_index
            total = len(session.questions)
            session.progress_percentage = int((next_index / total) * 100)
            return session.questions[next_index]

        # If at the end, mark completed
        session.current_question_index = len(session.questions)
        session.progress_percentage = 100
        session.status = "COMPLETED"
        session.ended_at = datetime.now(timezone.utc).isoformat()
        return None

    @classmethod
    def update_interview_progress(
        cls,
        session_id: str,
        answer_record: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Records the answer evaluation and updates overall interview completion status.
        """
        session = cls.get_session(session_id)

        if answer_record:
            session.history.append(answer_record)

        total_q = max(len(session.questions), 1)
        completed_q = len(session.history)
        progress = min(100, int((completed_q / total_q) * 100))
        session.progress_percentage = progress

        return {
            "session_id": session.session_id,
            "status": session.status,
            "current_question_index": session.current_question_index,
            "questions_completed": completed_q,
            "total_questions": total_q,
            "progress_percentage": progress,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }

    @classmethod
    def end_interview(cls, session_id: str) -> Dict[str, Any]:
        """
        Gracefully terminates an interview session and calculates summary metrics.
        """
        session = cls.get_session(session_id)
        session.status = "COMPLETED"
        session.ended_at = datetime.now(timezone.utc).isoformat()
        session.progress_percentage = 100

        total_questions_answered = len(session.history)
        scores = [h.get("score", 75) for h in session.history if isinstance(h, dict) and "score" in h]
        avg_score = round(sum(scores) / len(scores), 1) if scores else 80.0

        summary = {
            "session_id": session.session_id,
            "target_role": session.target_role,
            "status": "COMPLETED",
            "started_at": session.started_at,
            "ended_at": session.ended_at,
            "total_questions_planned": len(session.questions),
            "questions_answered": total_questions_answered,
            "average_performance_score": avg_score,
            "completion_rate": f"{session.progress_percentage}%"
        }
        session.final_summary = summary
        return summary
