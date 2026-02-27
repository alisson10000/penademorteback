from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.core.database import Base, engine
import app.db.base  # noqa: F401  # garante import dos models (User/Question/Answer/Admin)

from app.modules.survey.router import router as survey_router
from app.modules.admin.router import router as admin_router  # ✅ novo

app = FastAPI(title="PenaDeMorte API")

# ✅ cria tabelas (rápido pra começar). Depois você pode migrar com Alembic.
# Como app.db.base foi importado acima, Base.metadata já "enxerga" todos os models.
Base.metadata.create_all(bind=engine)

# ✅ Routers
app.include_router(survey_router)
app.include_router(admin_router)  # ✅ novo

@app.get("/", include_in_schema=False)
def root():
    # mantém o comportamento atual (abre /docs)
    return RedirectResponse(url="/docs")

@app.get("/health")
def health():
    return {"ok": True}