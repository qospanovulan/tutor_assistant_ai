from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Table, Column, Integer, String, DateTime, Boolean, ForeignKey, Text, JSON
)
from sqlalchemy.orm import registry, relationship

# Domain models (dataclasses)
from domain.models.students import (
    WebSession,
    Topic,
    TopicPrompt,
    ChatSession,
    Message,
    Lecture,
    Test,
    Question,
    QuestionOption,
    Answer,
    RemediationLecture,
)

mapper_registry = registry()
metadata = mapper_registry.metadata


# -----------------------------
# Tables
# -----------------------------
topics_table = Table(
    "topics",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String, nullable=False, unique=True),
    Column("description", Text, nullable=True),
    Column("grade_min", Integer, nullable=True),
    Column("grade_max", Integer, nullable=True),
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
)

topic_prompts_table = Table(
    "topic_prompts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("topic_id", ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("lecture_prompt_template", Text, nullable=True),
    Column("test_prompt_template", Text, nullable=True),
    Column("remediation_prompt_template", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
    Column("updated_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
)

web_sessions_table = Table(
    "web_sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("session_key", String, nullable=False, unique=True, index=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
    Column("last_seen_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
)

chat_sessions_table = Table(
    "chat_sessions",
    metadata,
    Column("id", Integer, primary_key=True),

    Column("web_session_id", ForeignKey("web_sessions.id", ondelete="CASCADE"), nullable=False),

    Column("student_name", String, nullable=False),
    Column("grade", Integer, nullable=False),
    Column("topic_id", ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False),
    Column("status", String, nullable=False),  # SessionStatus Literal in domain
    Column("is_active", Boolean, nullable=False, default=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
    Column("closed_at", DateTime(timezone=True), nullable=True),
)

messages_table = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
    Column("role", String, nullable=False),  # MessageRole Literal
    Column("kind", String, nullable=False),  # MessageKind Literal
    Column("content", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
)

lectures_table = Table(
    "lectures",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("topic_id", ForeignKey("topics.id", ondelete="RESTRICT"), nullable=False),
    Column("content_md", Text, nullable=False),
    Column("model_name", String, nullable=True),
    Column("prompt_version", String, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
)

tests_table = Table(
    "tests",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("num_questions", Integer, nullable=False, default=5),
    Column("status", String, nullable=False),  # TestStatus Literal
    Column("current_question_idx", Integer, nullable=False, default=1),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
    Column("finished_at", DateTime(timezone=True), nullable=True),
)

questions_table = Table(
    "questions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("test_id", ForeignKey("tests.id", ondelete="CASCADE"), nullable=False),
    Column("idx", Integer, nullable=False),  # 1..5; enforce unique(test_id, idx) in migration
    Column("type", String, nullable=False),  # QuestionType Literal
    Column("prompt", Text, nullable=False),
    Column("correct_answer", Text, nullable=False),
    Column("explanation", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
)

question_options_table = Table(
    "question_options",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("question_id", ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
    Column("label", String, nullable=False),  # "A"/"B"/"C"/"D"
    Column("text", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
)

answers_table = Table(
    "answers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("question_id", ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("session_id", ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
    Column("raw_message_id", ForeignKey("messages.id", ondelete="SET NULL"), nullable=True),
    Column("answer_text", Text, nullable=False),
    Column("is_correct", Boolean, nullable=False),
    Column("feedback_text", Text, nullable=True),
    Column("answered_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
)

remediation_lectures_table = Table(
    "remediation_lectures",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("session_id", ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("test_id", ForeignKey("tests.id", ondelete="CASCADE"), nullable=False, unique=True),
    Column("incorrect_question_ids", JSON, nullable=False),  # list[int] in domain
    Column("content_md", Text, nullable=False),
    Column("model_name", String, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False, default=datetime.utcnow),
)


# -----------------------------
# Mappers
# -----------------------------
def start_mappers() -> None:
    mapper_registry.map_imperatively(
        Topic,
        topics_table,
        properties={
            "sessions": relationship(
                "ChatSession",
                back_populates="topic",
                lazy="raise",
            ),
            "prompt": relationship(
                "TopicPrompt",
                back_populates="topic",
                uselist=False,
                lazy="raise",
                cascade="all, delete-orphan",
            ),
            "lectures": relationship(
                "Lecture",
                back_populates="topic",
                lazy="raise",
            ),
        },
    )

    mapper_registry.map_imperatively(
        TopicPrompt,
        topic_prompts_table,
        properties={
            "topic": relationship(
                "Topic",
                back_populates="prompt",
                lazy="raise",
            ),
        },
    )

    mapper_registry.map_imperatively(
        WebSession,
        web_sessions_table,
        properties={
            "chats": relationship(
                "ChatSession",
                back_populates="web_session",
                cascade="all, delete-orphan",
                lazy="raise",
            ),
        },
    )

    mapper_registry.map_imperatively(
        ChatSession,
        chat_sessions_table,
        properties={
            "web_session": relationship(
                "WebSession",
                back_populates="chats",
                lazy="raise",
            ),
            "topic": relationship(
                "Topic",
                back_populates="sessions",
                lazy="raise",
            ),
            "messages": relationship(
                "Message",
                back_populates="session",
                cascade="all, delete-orphan",
                lazy="raise",
            ),
            "lecture": relationship(
                "Lecture",
                back_populates="session",
                uselist=False,
                cascade="all, delete-orphan",
                lazy="raise",
            ),
            "test": relationship(
                "Test",
                back_populates="session",
                uselist=False,
                cascade="all, delete-orphan",
                lazy="raise",
            ),
            "remediation": relationship(
                "RemediationLecture",
                back_populates="session",
                uselist=False,
                cascade="all, delete-orphan",
                lazy="raise",
            ),
        },
    )

    mapper_registry.map_imperatively(
        Message,
        messages_table,
        properties={
            "session": relationship(
                "ChatSession",
                back_populates="messages",
                lazy="raise",
            ),
            "answer": relationship(
                "Answer",
                back_populates="raw_message",
                uselist=False,
                lazy="raise",
            ),
        },
    )

    mapper_registry.map_imperatively(
        Lecture,
        lectures_table,
        properties={
            "session": relationship(
                "ChatSession",
                back_populates="lecture",
                lazy="raise",
            ),
            "topic": relationship(
                "Topic",
                back_populates="lectures",
                lazy="raise",
            ),
        },
    )

    mapper_registry.map_imperatively(
        Test,
        tests_table,
        properties={
            "session": relationship(
                "ChatSession",
                back_populates="test",
                lazy="raise",
            ),
            "questions": relationship(
                "Question",
                back_populates="test",
                cascade="all, delete-orphan",
                order_by=questions_table.c.idx,
                lazy="raise",
            ),
            "remediation": relationship(
                "RemediationLecture",
                back_populates="test",
                uselist=False,
                lazy="raise",
            ),
        },
    )

    mapper_registry.map_imperatively(
        Question,
        questions_table,
        properties={
            "test": relationship(
                "Test",
                back_populates="questions",
                lazy="raise",
            ),
            "options": relationship(
                "QuestionOption",
                back_populates="question",
                cascade="all, delete-orphan",
                lazy="raise",
            ),
            "answer": relationship(
                "Answer",
                back_populates="question",
                uselist=False,
                lazy="raise",
            ),
        },
    )

    mapper_registry.map_imperatively(
        QuestionOption,
        question_options_table,
        properties={
            "question": relationship(
                "Question",
                back_populates="options",
                lazy="raise",
            ),
        },
    )

    mapper_registry.map_imperatively(
        Answer,
        answers_table,
        properties={
            "question": relationship(
                "Question",
                back_populates="answer",
                lazy="raise",
            ),
            "session": relationship(
                "ChatSession",
                lazy="raise",
            ),
            "raw_message": relationship(
                "Message",
                back_populates="answer",
                lazy="raise",
                foreign_keys=[answers_table.c.raw_message_id],
            ),
        },
    )

    mapper_registry.map_imperatively(
        RemediationLecture,
        remediation_lectures_table,
        properties={
            "session": relationship(
                "ChatSession",
                back_populates="remediation",
                lazy="raise",
            ),
            "test": relationship(
                "Test",
                back_populates="remediation",
                lazy="raise",
            ),
        },
    )
