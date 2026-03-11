from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdBase(BaseModel):
    tipo: str  # 'imagem' ou 'youtube'
    url: str
    link: Optional[str] = None
    question_id: int  # ✅ FK da pergunta dona da ad


class AdCreate(AdBase):
    created_by_id: int  # ID admin logado (injetado no service/router)


class AdUpdate(BaseModel):
    tipo: Optional[str] = None
    url: Optional[str] = None
    link: Optional[str] = None
    ativo: Optional[bool] = None
    question_id: Optional[int] = None  # permite trocar de pergunta (ou deixar igual)


class Ad(AdBase):
    id: int
    ativo: bool
    created_at: datetime
    created_by_id: int  # Visível na resposta

    class Config:
        from_attributes = True
