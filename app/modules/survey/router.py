from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import EmailStr
from sqlalchemy import select

from app.core.database import get_db
from app.modules.survey import schemas, service
from app.modules.survey.models import User

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.post("/enter", response_model=schemas.EnterOut)
def enter(payload: schemas.EnterIn, db: Session = Depends(get_db)):
    user_id = service.enter_with_email(db, payload.email)
    return {"user_id": user_id}


@router.get("/questions/next", response_model=schemas.NextQuestionOut)
def next_question(user_id: int, db: Session = Depends(get_db)):
    q = service.get_next_question(db, user_id)
    if not q:
        return {"question": None, "done": True}

    return {
        "question": {"id": q.id, "text": q.text, "order_index": q.order_index},
        "done": False,
    }


@router.post("/answers", response_model=schemas.AnswerOut)
def answer(payload: schemas.AnswerIn, db: Session = Depends(get_db)):
    service.save_answer(db, payload.user_id, payload.question_id, payload.answer_value)

    q = service.get_next_question(db, payload.user_id)
    if not q:
        return {"saved": True, "next_question": None, "done": True}

    return {
        "saved": True,
        "next_question": {"id": q.id, "text": q.text, "order_index": q.order_index},
        "done": False,
    }


@router.get("/stats")
def stats(question_id: int, db: Session = Depends(get_db)):
    return service.stats_for_question(db, question_id)


@router.get("/state", response_model=schemas.SurveyStateOut)
def state(
    db: Session = Depends(get_db),
    email: Optional[EmailStr] = None,
    user_id: Optional[int] = None,
):
    # ✅ Preferencial/seguro: usa email (não expõe user_id)
    if email is not None:
        uid = service.enter_with_email(db, str(email))
        return service.get_survey_state(db, uid)

    # ✅ Compatibilidade: permite user_id mas valida existência
    if user_id is None:
        raise HTTPException(status_code=400, detail="Informe email ou user_id")

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return service.get_survey_state(db, user_id)