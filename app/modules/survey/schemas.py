from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal, List


class EnterIn(BaseModel):
    email: EmailStr


class EnterOut(BaseModel):
    user_id: int


# ✅ novo: segmento de texto com estilo
class TextSegmentOut(BaseModel):
    text: str
    color: Optional[str] = None   # ex: "#0000FF"
    bold: Optional[bool] = None   # true/false


class QuestionOut(BaseModel):
    id: int
    text: str
    order_index: int

    # ✅ novo: rich text (sempre será lista na resposta)
    content: List[TextSegmentOut] = Field(default_factory=list)


class NextQuestionOut(BaseModel):
    question: Optional[QuestionOut] = None
    done: bool


class AnswerIn(BaseModel):
    user_id: int
    question_id: int
    answer_value: Literal["yes", "no"] = Field(..., description="yes/no")


class AnswerOut(BaseModel):
    saved: bool
    next_question: Optional[QuestionOut] = None
    done: bool


# ✅ NOVOS schemas para /survey/state

class AnsweredItemOut(BaseModel):
    question: QuestionOut
    answer_value: Literal["yes", "no"]


class SurveyStateOut(BaseModel):
    user_id: int
    answered_count: int
    total_active: int
    answered: List[AnsweredItemOut]
    next_question: Optional[QuestionOut] = None
    done: bool