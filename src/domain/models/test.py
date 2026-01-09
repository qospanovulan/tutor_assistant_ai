from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING
from domain.models.enums import Difficulty, TestSpecStatus, QuestionType

if TYPE_CHECKING:
    from domain.models.attempt import TestAttempt
    from domain.models.user import User


@dataclass
class TestSpec:
    id: int | None
    teacher_id: int
    name: str
    topic: str
    grade: int
    difficulty: Difficulty
    single_choice_count: int
    multi_choice_count: int
    open_count: int
    status: TestSpecStatus = TestSpecStatus.DRAFT
    created_at: datetime | None = None
    updated_at: datetime | None = None
    teacher: User | None = None
    questions: list[TestQuestion] = field(default_factory=list)
    test: Test | None = None


@dataclass
class Test:
    id: int | None
    spec_id: int
    is_active: bool = True
    version: int = 1
    published_at: datetime | None = None
    spec: TestSpec | None = None
    questions: list[TestQuestion] = field(default_factory=list)
    attempts: list[TestAttempt] = field(default_factory=list)


@dataclass
class TestQuestion:
    id: int | None
    # draft questions may have spec_id only; published questions will also have test_id
    spec_id: int
    test_id: int | None
    type: QuestionType
    question_text: str
    explanation: str | None = None
    difficulty: Difficulty | None = None
    points: int = 1
    position: int = 1
    is_deleted: bool = False
    created_at: datetime | None = None
    spec: TestSpec | None = None
    test: Test | None = None
    options: list[QuestionOption] = field(default_factory=list)
    open_key: OpenAnswerKey | None = None


@dataclass
class QuestionOption:
    id: int | None
    question_id: int
    option_text: str
    is_correct: bool
    position: int = 1
    question: TestQuestion | None = None


@dataclass
class OpenAnswerKey:
    question_id: int
    expected_answer: str | None = None
    rubric_json: dict | None = None
    question: TestQuestion | None = None
