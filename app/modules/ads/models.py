from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(50), nullable=False, index=True)   # 'imagem' ou 'youtube'
    url = Column(String(500), nullable=False)               # Caminho imagem ou ID YT
    link = Column(String(500), nullable=True)               # URL externa (landing page)
    ativo = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Quem criou a propaganda
    created_by_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    created_by = relationship("Admin", back_populates="ads")

    # ✅ FK para a pergunta dona desta ad
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    question = relationship("Question", back_populates="ads")
