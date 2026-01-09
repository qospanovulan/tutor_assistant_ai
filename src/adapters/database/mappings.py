from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Table, Column, Integer, String, DateTime, Boolean, Float, Text,
    ForeignKey, UniqueConstraint, CheckConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import registry, relationship
from sqlalchemy import Enum as SAEnum

from domain.models.user import User, StudentProfile
from domain.models.session import Session
from domain.models.test import (
    TestSpec, Test, TestQuestion, QuestionOption, OpenAnswerKey
)
from domain.models.attempt import TestAttempt, AttemptAnswer, AttemptSelectedOption
from domain.models.chat import ChatSession, ChatMessage
from domain.models.enums import (
    UserRole, Difficulty, TestSpecStatus, QuestionType,
    AttemptStatus, ChatKind, MessageRole
)

mapper_registry = registry()
metadata = mapper_registry.metadata

# ----------------------------
# USERS / STUDENTS
# ----------------------------
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(255), nullable=False, unique=True),
    Column("password_hash", String(255), nullable=False),
    Column("role", SAEnum(UserRole, name="user_role"), nullable=False),
    Column("full_name", String(255), nullable=True),
    Column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False),
)

student_profiles_table = Table(
    "student_profiles",
    metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("grade", Integer, nullable=False),
    CheckConstraint("grade >= 1 AND grade <= 12", name="ck_student_grade_range"),
)

# ----------------------------
# SESSIONS
# ----------------------------
sessions_table = Table(
    "user_sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("session_key", String(64), nullable=False, unique=True),
    Column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=True),
    Column("revoked_at", DateTime(timezone=True), nullable=True),
)

# ----------------------------
# TEST SPECS / TESTS
# ----------------------------
test_specs_table = Table(
    "test_specs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("teacher_id", ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
    Column("name", String(255), nullable=False),
    Column("topic", String(255), nullable=False),
    Column("grade", Integer, nullable=False),
    Column("difficulty", SAEnum(Difficulty, name="difficulty_level"), nullable=False),
    Column("single_choice_count", Integer, nullable=False, default=0),
    Column("multi_choice_count", Integer, nullable=False, default=0),
    Column("open_count", Integer, nullable=False, default=0),
    Column("status", SAEnum(TestSpecStatus, name="test_spec_status"), nullable=False, default=TestSpecStatus.DRAFT),
    Column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False),
    Column("updated_at", DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    CheckConstraint("grade >= 1 AND grade <= 12", name="ck_test_spec_grade_range"),
    CheckConstraint("single_choice_count >= 0", name="ck_test_spec_sc_nonneg"),
    CheckConstraint("multi_choice_count >= 0", name="ck_test_spec_mc_nonneg"),
    CheckConstraint("open_count >= 0", name="ck_test_spec_open_nonneg"),
)

tests_table = Table(
    "tests",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("spec_id", ForeignKey("test_specs.id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("version", Integer, nullable=False, default=1),
    Column("published_at", DateTime(timezone=True), nullable=True),
)

# ----------------------------
# QUESTIONS / OPTIONS
# ----------------------------
test_questions_table = Table(
    "test_questions",
    metadata,
    Column("id", Integer, primary_key=True),

    # Draft questions: spec_id NOT NULL, test_id NULL
    # Published questions: spec_id NOT NULL, test_id NOT NULL
    Column("spec_id", ForeignKey("test_specs.id", ondelete="CASCADE"), nullable=False),
    Column("test_id", ForeignKey("tests.id", ondelete="CASCADE"), nullable=True),

    Column("type", SAEnum(QuestionType, name="question_type"), nullable=False),
    Column("question_text", Text, nullable=False),
    Column("explanation", Text, nullable=True),
    Column("difficulty", SAEnum(Difficulty, name="question_difficulty"), nullable=True),
    Column("points", Integer, nullable=False, default=1),
    Column("position", Integer, nullable=False, default=1),
    Column("is_deleted", Boolean, nullable=False, default=False),
    Column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False),

    CheckConstraint("points >= 0", name="ck_question_points_nonneg"),
    CheckConstraint("position >= 1", name="ck_question_position_min1"),
)

question_options_table = Table(
    "question_options",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("question_id", ForeignKey("test_questions.id", ondelete="CASCADE"), nullable=False),
    Column("option_text", Text, nullable=False),
    Column("is_correct", Boolean, nullable=False),
    Column("position", Integer, nullable=False, default=1),
    CheckConstraint("position >= 1", name="ck_option_position_min1"),
)

open_answer_keys_table = Table(
    "open_answer_keys",
    metadata,
    Column("question_id", ForeignKey("test_questions.id", ondelete="CASCADE"), primary_key=True),
    Column("expected_answer", Text, nullable=True),
    Column("rubric_json", JSONB, nullable=True),
)

# ----------------------------
# ATTEMPTS / ANSWERS
# ----------------------------
test_attempts_table = Table(
    "test_attempts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("test_id", ForeignKey("tests.id", ondelete="RESTRICT"), nullable=False),
    Column("student_id", ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),

    Column("status", SAEnum(AttemptStatus, name="attempt_status"), nullable=False, default=AttemptStatus.IN_PROGRESS),
    Column("score", Float, nullable=True),
    Column("max_score", Float, nullable=True),
    Column("topic_feedback", Text, nullable=True),

    Column("started_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False),
    Column("submitted_at", DateTime(timezone=True), nullable=True),
    Column("graded_at", DateTime(timezone=True), nullable=True),

    Column("review_chat_session_id", ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True),
)

attempt_answers_table = Table(
    "attempt_answers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("attempt_id", ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False),
    Column("question_id", ForeignKey("test_questions.id", ondelete="RESTRICT"), nullable=False),

    Column("answer_text", Text, nullable=True),
    Column("is_correct", Boolean, nullable=True),
    Column("points_awarded", Float, nullable=True),

    UniqueConstraint("attempt_id", "question_id", name="uq_attempt_question_once"),
)

attempt_selected_options_table = Table(
    "attempt_selected_options",
    metadata,
    Column("attempt_answer_id", ForeignKey("attempt_answers.id", ondelete="CASCADE"), primary_key=True),
    Column("option_id", ForeignKey("question_options.id", ondelete="RESTRICT"), primary_key=True),
)

# ----------------------------
# CHAT
# ----------------------------
chat_sessions_table = Table(
    "chat_sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
    Column("kind", SAEnum(ChatKind, name="chat_kind"), nullable=False, default=ChatKind.ASSISTANT_CHAT),
    Column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False),
)

chat_messages_table = Table(
    "chat_messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
    Column("role", SAEnum(MessageRole, name="message_role"), nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), default=datetime.utcnow, nullable=False),
)

# ============================================================
# MAPPERS (imperative)
# ============================================================
def start_mappers() -> None:
    # Users
    mapper_registry.map_imperatively(
        User,
        users_table,
        properties={
            "student_profile": relationship(
                StudentProfile,
                uselist=False,
                back_populates="user",
                cascade="all, delete-orphan",
            ),
            "sessions": relationship(
                Session,
                back_populates="user",
                cascade="all, delete-orphan",
            ),
        },
    )

    mapper_registry.map_imperatively(
        StudentProfile,
        student_profiles_table,
        properties={
            "user": relationship(User, back_populates="student_profile"),
        },
    )

    mapper_registry.map_imperatively(
        Session,
        sessions_table,
        properties={
            "user": relationship(User, back_populates="sessions"),
        },
    )

    # Test specs
    mapper_registry.map_imperatively(
        TestSpec,
        test_specs_table,
        properties={
            "teacher": relationship(User, foreign_keys=[test_specs_table.c.teacher_id]),
            "questions": relationship(
                TestQuestion,
                primaryjoin=test_specs_table.c.id == test_questions_table.c.spec_id,
                back_populates="spec",
                cascade="all, delete-orphan",
            ),
            "test": relationship(
                Test,
                uselist=False,
                back_populates="spec",
                cascade="all, delete-orphan",
            ),
        },
    )

    mapper_registry.map_imperatively(
        Test,
        tests_table,
        properties={
            "spec": relationship(TestSpec, back_populates="test"),
            "questions": relationship(
                TestQuestion,
                primaryjoin=tests_table.c.id == test_questions_table.c.test_id,
                back_populates="test",
            ),
            "attempts": relationship(
                TestAttempt,
                back_populates="test",
            ),
        },
    )

    # Questions
    mapper_registry.map_imperatively(
        TestQuestion,
        test_questions_table,
        properties={
            "spec": relationship(TestSpec, back_populates="questions"),
            "test": relationship(Test, back_populates="questions"),
            "options": relationship(
                QuestionOption,
                back_populates="question",
                cascade="all, delete-orphan",
                order_by=question_options_table.c.position,
            ),
            "open_key": relationship(
                OpenAnswerKey,
                uselist=False,
                back_populates="question",
                cascade="all, delete-orphan",
            ),
        },
    )

    mapper_registry.map_imperatively(
        QuestionOption,
        question_options_table,
        properties={
            "question": relationship(TestQuestion, back_populates="options"),
        },
    )

    mapper_registry.map_imperatively(
        OpenAnswerKey,
        open_answer_keys_table,
        properties={
            "question": relationship(TestQuestion, back_populates="open_key"),
        },
    )

    # Attempts
    mapper_registry.map_imperatively(
        TestAttempt,
        test_attempts_table,
        properties={
            "test": relationship(Test, back_populates="attempts"),
            "student": relationship(User, foreign_keys=[test_attempts_table.c.student_id]),
            "answers": relationship(
                AttemptAnswer,
                back_populates="attempt",
                cascade="all, delete-orphan",
            ),
            "review_chat_session": relationship(
                ChatSession,
                foreign_keys=[test_attempts_table.c.review_chat_session_id],
            ),
        },
    )

    mapper_registry.map_imperatively(
        AttemptAnswer,
        attempt_answers_table,
        properties={
            "attempt": relationship(TestAttempt, back_populates="answers"),
            "question": relationship(TestQuestion, foreign_keys=[attempt_answers_table.c.question_id]),
            "selected_options": relationship(
                AttemptSelectedOption,
                back_populates="attempt_answer",
                cascade="all, delete-orphan",
            ),
        },
    )

    mapper_registry.map_imperatively(
        AttemptSelectedOption,
        attempt_selected_options_table,
        properties={
            "attempt_answer": relationship(AttemptAnswer, back_populates="selected_options"),
            "option": relationship(QuestionOption),
        },
    )

    # Chat
    mapper_registry.map_imperatively(
        ChatSession,
        chat_sessions_table,
        properties={
            "user": relationship(User),
            "messages": relationship(
                ChatMessage,
                back_populates="session",
                cascade="all, delete-orphan",
                order_by=chat_messages_table.c.created_at,
            ),
        },
    )

    mapper_registry.map_imperatively(
        ChatMessage,
        chat_messages_table,
        properties={
            "session": relationship(ChatSession, back_populates="messages"),
        },
    )
