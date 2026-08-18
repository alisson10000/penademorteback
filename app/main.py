import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine
import app.db.base  # noqa

from app.modules.survey.router import router as survey_router
from app.modules.admin.router import router as admin_router
from app.modules.stats.router import router as stats_router
from app.modules.ads.router import router as ads_router


ROOT_PATH = os.getenv("ROOT_PATH", "")

STATIC_DIR = os.getenv("STATIC_DIR", "/opt/penademorteback/static")

app = FastAPI(
    title="PenaDeMorte API",
    root_path=ROOT_PATH,
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",

    # Front acessado diretamente pelo IP da VPS
    "http://177.153.66.136:3000",

    # Domínios
    "https://srv1399917.hstgr.cloud",
    "https://penademorte.org",
    "https://www.penademorte.org",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

print(f"📁 Static path: {STATIC_DIR}")
print(f"📁 Existe? {os.path.exists(STATIC_DIR)}")

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)

print("✅ Static montado")

videos_path = os.path.join(STATIC_DIR, "videos")

if os.path.exists(videos_path):
    videos = os.listdir(videos_path)
    print(f"📹 Vídeos na pasta: {videos}")
else:
    print(f"⚠️ Pasta videos não existe em {videos_path}")

app.include_router(survey_router)
app.include_router(admin_router)
app.include_router(
    stats_router,
    prefix="/admin/stats",
    tags=["Admin Stats"],
)
app.include_router(
    ads_router,
    prefix="/ads",
    tags=["Ads"],
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(
        url=f"{ROOT_PATH}/docs" if ROOT_PATH else "/docs"
    )


@app.get("/health")
def health():
    return {"ok": True}