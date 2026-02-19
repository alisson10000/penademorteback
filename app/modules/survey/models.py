from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)  # ✅ aqui
    active = Column(Boolean, default=True, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)

class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    answer_value = Column(String(3), nullable=False)  # "yes" | "no"

    __table_args__ = (
        UniqueConstraint("user_id", "question_id", name="uk_answers_user_question"),
    )

    user = relationship("User")
    question = relationship("Question")
