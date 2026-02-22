from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.modules.survey.models import User, Question, Answer


def normalize_email(email: str) -> str:
    return email.strip().lower()


def ensure_content(q: Question):
    """
    Garante que sempre exista content no formato lista de segmentos.
    - Se q.content existir (JSON), usa ele.
    - Se não existir (NULL), cria fallback com o text inteiro.
    """
    if q is None:
        return None

    if q.content:
        return q.content

    return [{"text": q.text}]


def question_to_dict(q: Question) -> dict:
    """
    Retorno padronizado para QuestionOut (agora com content).
    Mantém text por compatibilidade.
    """
    return {
        "id": q.id,
        "text": q.text,
        "order_index": q.order_index,
        "content": ensure_content(q),
    }


def enter_with_email(db: Session, email: str) -> int:
    email = normalize_email(email)

    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user:
        return user.id

    user = User(email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id


def get_next_question(db: Session, user_id: int):
    # Próxima pergunta ativa que ainda não foi respondida pelo user_id
    subq = select(Answer.question_id).where(Answer.user_id == user_id)

    q = db.execute(
        select(Question)
        .where(Question.active == True)  # noqa: E712
        .where(~Question.id.in_(subq))
        .order_by(Question.order_index.asc())
        .limit(1)
    ).scalar_one_or_none()

    return q


def save_answer(db: Session, user_id: int, question_id: int, answer_value: str) -> None:
    # Upsert: se já existe resposta, atualiza
    existing = db.execute(
        select(Answer).where(
            Answer.user_id == user_id,
            Answer.question_id == question_id,
        )
    ).scalar_one_or_none()

    if existing:
        existing.answer_value = answer_value
    else:
        db.add(Answer(user_id=user_id, question_id=question_id, answer_value=answer_value))

    db.commit()


def stats_for_question(db: Session, question_id: int):
    # Retorna totais e percentuais de yes/no
    total = db.execute(
        select(func.count(Answer.id)).where(Answer.question_id == question_id)
    ).scalar_one()

    if not total:
        return {"question_id": question_id, "total": 0, "items": []}

    rows = db.execute(
        select(Answer.answer_value, func.count(Answer.id))
        .where(Answer.question_id == question_id)
        .group_by(Answer.answer_value)
        .order_by(func.count(Answer.id).desc())
    ).all()

    items = []
    for val, cnt in rows:
        items.append({
            "answer_value": val,
            "total": int(cnt),
            "percentual": round((cnt * 100.0) / total, 2),
        })

    return {"question_id": question_id, "total": int(total), "items": items}


def get_survey_state(db: Session, user_id: int):
    # total de perguntas ativas
    total_active = db.execute(
        select(func.count(Question.id)).where(Question.active == True)  # noqa: E712
    ).scalar_one()

    # lista de respondidas (Question + Answer.answer_value)
    rows = db.execute(
        select(Question, Answer.answer_value)
        .join(Answer, Answer.question_id == Question.id)
        .where(Answer.user_id == user_id)
        .order_by(Question.order_index.asc())
    ).all()

    answered = []
    for q, val in rows:
        answered.append(
            {
                "question": question_to_dict(q),
                "answer_value": val,
            }
        )

    # próxima pendente
    next_q = get_next_question(db, user_id)
    done = next_q is None

    return {
        "user_id": user_id,
        "answered_count": len(answered),
        "total_active": int(total_active),
        "answered": answered,
        "next_question": None if done else question_to_dict(next_q),
        "done": done,
    }