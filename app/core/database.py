from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # ✅ VPS OK
    pool_recycle=3600,   # ✅ Conexões recicladas
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# IMPORTA MODELS (você já tem)
from app.modules.survey.models import User, Question, Answer  # noqa: F401
from app.modules.admin.models import Admin  # noqa: F401

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🚀 CRIA TUDO NO BANCO!
Base.metadata.create_all(bind=engine)
