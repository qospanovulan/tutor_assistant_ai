from __future__ import annotations

from enum import Enum


class UserRole(str, Enum):
    TEACHER = "teacher"
    STUDENT = "student"


class Difficulty(str, Enum):
    EASY = "easy"
    MIDDLE = "middle"
    HARD = "hard"
    EXTRA = "extra"


class TestSpecStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY_FOR_REVIEW = "ready_for_review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class QuestionType(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTI_CHOICE = "multi_choice"
    OPEN = "open"


class AttemptStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    GRADED = "graded"


class ChatKind(str, Enum):
    ASSISTANT_CHAT = "assistant_chat"
    TEST_REVIEW = "test_review"
    OTHER = "other"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
