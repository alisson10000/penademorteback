from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.dependencies import require_admin

from .service import get_overview, get_by_question
from .schemas import StatsOverviewOut, StatsByQuestionOut

router = APIRouter()

@router.get("/overview", response_model=StatsOverviewOut)
def stats_overview(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return get_overview(db)

@router.get("/by-question", response_model=list[StatsByQuestionOut])
def stats_by_question(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return get_by_question(db)