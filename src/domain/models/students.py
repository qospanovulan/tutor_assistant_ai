from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import NewType, Literal

# -----------------------------
# IDs (NewType)
# -----------------------------
TopicId = NewType("TopicId", int)
TopicPromptId = NewType("TopicPromptId", int)

WebSessionId = NewType("WebSessionId", int)
ChatSessionId = NewType("ChatSessionId", int)
MessageId = NewType("MessageId", int)

LectureId = NewType("LectureId", int)

TestId = NewType("TestId", int)
QuestionId = NewType("QuestionId", int)
QuestionOptionId = NewType("QuestionOptionId", int)
AnswerId = NewType("AnswerId", int)

RemediationLectureId = NewType("RemediationLectureId", int)

# -----------------------------
# Enums as Literals (simple)
# -----------------------------
SessionStatus = Literal[
    "new",
    "lecture_generated",
    "awaiting_test_consent",
    "in_test",
    "remediation_generated",
    "closed",
]

MessageRole = Literal["student", "assistant", "system"]

MessageKind = Literal[
    "input",
    "lecture",
    "test_prompt",
    "question",
    "feedback",
    "remediation",
    "control",
]

TestStatus = Literal["created", "in_progress", "finished"]

QuestionType = Literal["mcq", "true_false", "short"]


# -----------------------------
# Dataclasses (Domain Models)
# -----------------------------
@dataclass
class Topic:
    id: TopicId | None
    title: str
    description: str | None
    grade_min: int | None
    grade_max: int | None
    is_active: bool
    created_at: datetime


@dataclass
class TopicPrompt:
    id: TopicPromptId | None
    topic_id: TopicId
    lecture_prompt_template: str | None
    test_prompt_template: str | None
    remediation_prompt_template: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class WebSession:
    id: WebSessionId | None
    session_key: str
    created_at: datetime
    last_seen_at: datetime


@dataclass
class ChatSession:
    id: ChatSessionId | None
    web_session_id: WebSessionId
    student_name: str
    grade: int
    topic_id: TopicId
    status: SessionStatus
    is_active: bool
    created_at: datetime
    closed_at: datetime | None


@dataclass
class Message:
    id: MessageId | None
    session_id: ChatSessionId
    role: MessageRole
    kind: MessageKind
    content: str
    created_at: datetime


@dataclass
class Lecture:
    id: LectureId | None
    session_id: ChatSessionId
    topic_id: TopicId
    content_md: str
    model_name: str | None
    prompt_version: str | None
    created_at: datetime


@dataclass
class Test:
    id: TestId | None
    session_id: ChatSessionId
    num_questions: int
    status: TestStatus
    current_question_idx: int
    created_at: datetime
    finished_at: datetime | None


@dataclass
class Question:
    id: QuestionId | None
    test_id: TestId
    idx: int  # 1..5
    type: QuestionType
    prompt: str
    correct_answer: str
    explanation: str | None
    created_at: datetime


@dataclass
class QuestionOption:
    id: QuestionOptionId | None
    question_id: QuestionId
    label: str  # "A"/"B"/"C"/"D"
    text: str
    created_at: datetime


@dataclass
class Answer:
    id: AnswerId | None
    question_id: QuestionId
    session_id: ChatSessionId
    raw_message_id: MessageId | None
    answer_text: str
    is_correct: bool
    feedback_text: str | None
    answered_at: datetime


@dataclass
class RemediationLecture:
    id: RemediationLectureId | None
    session_id: ChatSessionId
    test_id: TestId
    incorrect_question_ids: list[int]  # store as list in domain, jsonb in db
    content_md: str
    model_name: str | None
    created_at: datetime
