from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import EmailStr
from sqlalchemy import select
from app.core.database import get_db
from app.modules.survey import schemas, service
from app.modules.survey.models import User, Question

router = APIRouter(prefix="/survey", tags=["Survey"])


@router.post("/enter", response_model=schemas.EnterOut)
def enter(payload: schemas.EnterIn, db: Session = Depends(get_db)):
    userid = service.enter_with_email(db, payload.email)
    return {"userid": userid}


@router.get("/questions", response_model=List[schemas.QuestionOut])
def list_all_questions(db: Session = Depends(get_db)):
    """
    ✅ NOVO: Lista TODAS as perguntas para admin/dropdown
    """
    questions = db.query(Question).order_by(Question.order_index).all()
    return [service.question_to_dict(q) for q in questions]


@router.get("/questions/next", response_model=schemas.NextQuestionOut)
def next_question(userid: int, db: Session = Depends(get_db)):
    q = service.get_next_question(db, userid)
    if not q:
        return {"question": None, "done": True}
    return {"question": service.question_to_dict(q), "done": False}


@router.post("/answers", response_model=schemas.AnswerOut)
def answer(payload: schemas.AnswerIn, db: Session = Depends(get_db)):
    service.save_answer(db, payload.userid, payload.questionid, payload.answervalue)
    q = service.get_next_question(db, payload.userid)
    if not q:
        return {"saved": True, "nextquestion": None, "done": True}
    return {"saved": True, "nextquestion": service.question_to_dict(q), "done": False}


@router.get("/stats")
def stats(question_id: int, db: Session = Depends(get_db)):
    return service.stats_for_question(db, question_id)


@router.get("/state", response_model=schemas.SurveyStateOut)
def state(
    db: Session = Depends(get_db),
    email: Optional[EmailStr] = None,
    userid: Optional[int] = None,
):
    """
    Retorna estado do survey (respondidas, próxima, etc)
    """
    if email is not None:
        uid = service.enter_with_email(db, str(email))
        return service.get_survey_state(db, uid)
    
    if userid is None:
        raise HTTPException(status_code=400, detail="Informe email ou userid")
    
    user = db.execute(select(User).where(User.id == userid)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    return service.get_survey_state(db, userid)
