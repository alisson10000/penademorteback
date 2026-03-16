from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AdBase(BaseModel):
    tipo: str  # 'image', 'youtube' ou 'video'
    url: str
    link: Optional[str] = None
    question_id: int


class AdCreate(AdBase):
    created_by_id: int


class AdUpdate(BaseModel):
    tipo: Optional[str] = None
    url: Optional[str] = None
    link: Optional[str] = None
    ativo: Optional[bool] = None
    question_id: Optional[int] = None


class Ad(AdBase):
    id: int
    ativo: bool
    created_at: datetime
    created_by_id: int

    class Config:
        from_attributes = True
