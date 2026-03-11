from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    Text,
    JSON,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)

    # opcional (não quebra): facilita user.answers
    answers = relationship(
        "Answer",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)

    # mantém o que já existe e já funciona
    text = Column(Text, nullable=False)

    # rich text em JSON (pode ser NULL para perguntas antigas)
    # Ex: [{"text":"...", "color":"#0000FF", "bold": true}, ...]
    content = Column(JSON, nullable=True)

    active = Column(Boolean, default=True, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)

    # ✅ novo apenas no ORM: lista de ads ligadas a esta pergunta
    ads = relationship("Ad", back_populates="question")

    # opcional (não quebra): facilita question.answers
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # "yes" | "no" (ou outros que você usar)
    answer_value = Column(String(3), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uk_answers_user_question"),
    )

    # mantém relacionamento funcional, agora com back_populates
    user = relationship("User", back_populates="answers")
    question = relationship("Question", back_populates="answers")
