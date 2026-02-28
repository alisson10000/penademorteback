from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.modules.survey.models import Answer, Question


def _safe_int(v) -> int:
    return int(v or 0)


def _pct(part: int, total: int) -> float:
    if not total:
        return 0.0
    return round((part / total) * 100.0, 2)


def _questions_total(db: Session) -> int:
    # usa questions (mais correto)
    return _safe_int(db.query(func.count(Question.id)).scalar())


def get_by_question(db: Session):
    """
    Retorna estatística por pergunta + texto (e content JSON).
    Considera apenas perguntas que possuem respostas.
    """

    rows = (
        db.query(
            Answer.question_id.label("question_id"),
            Question.text.label("question_text"),
            Question.content.label("question_content"),
            func.count(Answer.id).label("total_responses"),
            func.sum(case((Answer.answer_value == "yes", 1), else_=0)).label("yes_responses"),
            func.sum(case((Answer.answer_value == "no", 1), else_=0)).label("no_responses"),
        )
        .join(Question, Question.id == Answer.question_id)
        .group_by(Answer.question_id, Question.text, Question.content)
        .order_by(Answer.question_id.asc())
        .all()
    )

    out = []
    for r in rows:
        total = _safe_int(r.total_responses)
        yes = _safe_int(r.yes_responses)
        no = _safe_int(r.no_responses)

        out.append(
            {
                "question_id": int(r.question_id),
                "question_text": r.question_text,
                "question_content": r.question_content,
                "total_responses": total,
                "yes_responses": yes,
                "no_responses": no,
                "yes_percent": _pct(yes, total),
                "no_percent": _pct(no, total),
            }
        )

    return out


def get_overview(db: Session):
    """
    Overview geral:
    - total/yes/no + %
    - formulários completos/incompletos (por user_id)
    - estatística por pergunta com texto
    """

    # Totais gerais
    total_responses = _safe_int(db.query(func.count(Answer.id)).scalar())

    yes_responses = _safe_int(
        db.query(func.count(Answer.id)).filter(Answer.answer_value == "yes").scalar()
    )

    no_responses = _safe_int(
        db.query(func.count(Answer.id)).filter(Answer.answer_value == "no").scalar()
    )

    # Total de perguntas
    questions_total = _questions_total(db)

    # Formulários = respondentes únicos (users que responderam ao menos 1)
    total_forms = _safe_int(db.query(func.count(func.distinct(Answer.user_id))).scalar())

    # Completo = respondeu todas as perguntas (COUNT DISTINCT question_id == questions_total)
    complete_forms = 0
    if questions_total > 0:
        subq = (
            db.query(
                Answer.user_id.label("user_id"),
                func.count(func.distinct(Answer.question_id)).label("answered"),
            )
            .group_by(Answer.user_id)
            .subquery()
        )

        complete_forms = _safe_int(
            db.query(func.count())
            .select_from(subq)
            .filter(subq.c.answered == questions_total)
            .scalar()
        )

    incomplete_forms = max(total_forms - complete_forms, 0)

    # Por pergunta (com texto)
    by_question = get_by_question(db)

    return {
        # ✅ mantém compatível
        "total_responses": total_responses,
        "yes_responses": yes_responses,
        "no_responses": no_responses,

        # ✅ percentuais gerais
        "yes_percent": _pct(yes_responses, total_responses),
        "no_percent": _pct(no_responses, total_responses),

        "forms": {
            "total_forms": total_forms,
            "complete_forms": complete_forms,
            "incomplete_forms": incomplete_forms,
            "complete_percent": _pct(complete_forms, total_forms),
            "incomplete_percent": _pct(incomplete_forms, total_forms),
            "questions_total": questions_total,
        },

        "by_question": by_question,
    }