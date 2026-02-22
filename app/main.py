from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.database import Base, engine
import app.db.base  # noqa: F401  # garante import dos models

from app.modules.survey.router import router as survey_router

app = FastAPI(title="PenaDeMorte API")

# cria tabelas (rápido pra começar). Depois você pode migrar com Alembic.
Base.metadata.create_all(bind=engine)

app.include_router(survey_router)

@app.get("/", include_in_schema=False)
def root():
    # ✅ opção 1: redireciona para a doc
    return RedirectResponse(url="/docs")

    # ✅ opção 2 (se preferir JSON em vez de redirect):
    # return {"status": "ok", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"ok": True}