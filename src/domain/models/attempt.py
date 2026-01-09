from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING
from domain.models.enums import AttemptStatus

if TYPE_CHECKING:
    from domain.models.chat import ChatSession
    from domain.models.test import QuestionOption, Test, TestQuestion
    from domain.models.user import User


@dataclass
class TestAttempt:
    id: int | None
    test_id: int
    student_id: int
    status: AttemptStatus = AttemptStatus.IN_PROGRESS
    score: float | None = None
    max_score: float | None = None
    topic_feedback: str | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    submitted_at: datetime | None = None
    graded_at: datetime | None = None
    review_chat_session_id: int | None = None
    test: Test | None = None
    student: User | None = None
    answers: list[AttemptAnswer] = field(default_factory=list)
    review_chat_session: ChatSession | None = None


@dataclass
class AttemptAnswer:
    id: int | None
    attempt_id: int
    question_id: int
    answer_text: str | None = None
    is_correct: bool | None = None
    points_awarded: float | None = None
    attempt: TestAttempt | None = None
    question: TestQuestion | None = None
    selected_options: list[AttemptSelectedOption] = field(default_factory=list)


@dataclass
class AttemptSelectedOption:
    attempt_answer_id: int
    option_id: int
    attempt_answer: AttemptAnswer | None = None
    option: QuestionOption | None = None
