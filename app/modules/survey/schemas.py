from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal

class EnterIn(BaseModel):
    email: EmailStr

class EnterOut(BaseModel):
    user_id: int

class QuestionOut(BaseModel):
    id: int
    text: str
    order_index: int

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
