from app.core.database import engine
from app.db.base import Base  # garante que todos models foram importados

def init_db():
    Base.metadata.create_all(bind=engine)