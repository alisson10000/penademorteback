from sqlalchemy.orm import Session
import random
import os
from pathlib import Path

from . import models, schemas


def get_ads(db: Session, skip: int = 0, limit: int = 100, ativo_only: bool = True):
    query = db.query(models.Ad)
    if ativo_only:
        query = query.filter(models.Ad.ativo == True)
    return query.offset(skip).limit(limit).all()


def get_ad(db: Session, ad_id: int):
    return db.query(models.Ad).filter(models.Ad.id == ad_id).first()


def get_random_active_ad(db: Session):
    ads = db.query(models.Ad).filter(models.Ad.ativo == True).all()
    return random.choice(ads) if ads else None


def create_ad(db: Session, ad: schemas.AdCreate):
    db_ad = models.Ad(**ad.dict())
    db.add(db_ad)
    db.commit()
    db.refresh(db_ad)
    return db_ad


def update_ad(db: Session, ad_id: int, ad_update: schemas.AdUpdate):
    db_ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if db_ad:
        update_data = ad_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ad, field, value)
        db.commit()
        db.refresh(db_ad)
    return db_ad


def delete_ad(db: Session, ad_id: int):
    db_ad = db.query(models.Ad).filter(models.Ad.id == ad_id).first()
    if db_ad:
        # ✅ Deletar arquivo físico se for image ou video hospedado
        if db_ad.tipo in ["image", "video"] and db_ad.url.startswith("/static/"):
            try:
                # Caminho base do projeto (3 níveis acima: service.py -> ads -> modules -> app)
                base_path = Path(__file__).parent.parent.parent
                file_path = base_path / db_ad.url.lstrip("/")
                
                # Remove arquivo se existir
                if file_path.exists() and file_path.is_file():
                    os.remove(file_path)
                    print(f"✅ Arquivo deletado: {file_path}")
                else:
                    print(f"⚠️ Arquivo não encontrado: {file_path}")
            except Exception as e:
                print(f"⚠️ Erro ao deletar arquivo: {e}")
                # Não falha se der erro ao deletar arquivo físico
        
        # Deleta registro do banco
        db.delete(db_ad)
        db.commit()
        return True
    return False
