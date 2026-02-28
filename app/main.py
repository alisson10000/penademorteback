from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
import app.db.base  # noqa: F401

from app.modules.survey.router import router as survey_router
from app.modules.admin.router import router as admin_router


app = FastAPI(
    title="PenaDeMorte API",
    root_path="/api",  # ✅ essencial atrás do Caddy em /api/*
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

Base.metadata.create_all(bind=engine)

app.include_router(survey_router)
app.include_router(admin_router)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")  # com root_path vira /api/docs automaticamente

@app.get("/health")
def health():
    return {"ok": True}