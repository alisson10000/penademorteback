import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
import app.db.base  # noqa: F401

from app.modules.survey.router import router as survey_router
from app.modules.admin.router import router as admin_router
from app.modules.stats.router import router as stats_router
from app.modules.ads.router import router as ads_router


# Em produção atrás do Caddy em /api/*:
#   export ROOT_PATH=/api
# Em dev local:
#   ROOT_PATH vazio (padrão) para não gerar /api/api
ROOT_PATH = os.getenv("ROOT_PATH", "")

app = FastAPI(
    title="PenaDeMorte API",
    root_path=ROOT_PATH,
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://srv1399917.hstgr.cloud",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# mantém como está no seu projeto
Base.metadata.create_all(bind=engine)

# routers principais já existentes
app.include_router(survey_router)
app.include_router(admin_router)

# stats router em /admin/stats (ou /api/admin/stats em prod)
app.include_router(
    stats_router,
    prefix="/admin/stats",
    tags=["Admin Stats"],
)

# Ads router: acesso em /ads/* (ou /api/ads/* em prod)
app.include_router(
    ads_router,
    prefix="/ads",
    tags=["Ads"],
)

@app.get("/", include_in_schema=False)
def root():
    # redireciona para o docs respeitando o root_path
    return RedirectResponse(url=f"{ROOT_PATH}/docs" if ROOT_PATH else "/docs")

@app.get("/health")
def health():
    return {"ok": True}
