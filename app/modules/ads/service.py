from sqlalchemy.orm import Session
import random

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
        db.delete(db_ad)
        db.commit()
        return True
    return False
