from fastapi import FastAPI
from app.core.database import Base, engine
import app.db.base  # noqa: F401  # garante import dos models

from app.modules.survey.router import router as survey_router

app = FastAPI(title="PenaDeMorte API")

# cria tabelas (rápido pra começar). Depois você pode migrar com Alembic.
Base.metadata.create_all(bind=engine)

app.include_router(survey_router)

@app.get("/health")
def health():
    return {"ok": True}
