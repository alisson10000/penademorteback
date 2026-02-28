from typing import List, Optional, Any
from pydantic import BaseModel


class StatsByQuestionOut(BaseModel):
    question_id: int
    question_text: str
    question_content: Optional[Any] = None  # JSON opcional (pode ser dict/list)

    total_responses: int
    yes_responses: int
    no_responses: int
    yes_percent: float
    no_percent: float


class StatsFormsOut(BaseModel):
    total_forms: int
    complete_forms: int
    incomplete_forms: int
    complete_percent: float
    incomplete_percent: float
    questions_total: int


class StatsOverviewOut(BaseModel):
    # ✅ mantém os campos antigos
    total_responses: int
    yes_responses: int
    no_responses: int

    # ✅ extras úteis
    yes_percent: float
    no_percent: float

    forms: StatsFormsOut
    by_question: List[StatsByQuestionOut]