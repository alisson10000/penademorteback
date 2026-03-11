from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.modules.admin.dependencies import get_current_admin
from . import schemas, service


router = APIRouter(prefix="/ads", tags=["Ads"])


# ===========================
# READ - SEM AUTENTICAÇÃO
# ===========================
@router.get("/", response_model=List[schemas.Ad])
def read_ads(
    skip: int = 0,
    limit: int = 100,
    ativo_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    Lista ads (ativas por padrão)
    """
    ads = service.get_ads(db, skip=skip, limit=limit, ativo_only=ativo_only)
    return ads


@router.get("/random", response_model=schemas.Ad)
def read_random_ad(db: Session = Depends(get_db)):
    """
    Puxa ad ativa randômica (para mobile!)
    """
    ad = service.get_random_active_ad(db)
    if ad is None:
        raise HTTPException(status_code=404, detail="No active ads")
    return ad


@router.get("/{ad_id}", response_model=schemas.Ad)
def read_ad(ad_id: int, db: Session = Depends(get_db)):
    """
    Busca ad por ID
    """
    ad = service.get_ad(db, ad_id=ad_id)
    if ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad


# ===========================
# CREATE - COM AUTENTICAÇÃO
# ===========================
@router.post("/", response_model=schemas.Ad, status_code=status.HTTP_201_CREATED)
def create_ad(
    ad_in: schemas.AdCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Cria nova ad (requer autenticação de admin)
    """
    return service.create_ad(db=db, ad=ad_in)


# ===========================
# UPDATE - COM AUTENTICAÇÃO
# ===========================
@router.put("/{ad_id}", response_model=schemas.Ad)
def update_ad(
    ad_id: int,
    ad_update: schemas.AdUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Atualiza ad existente (requer autenticação de admin)
    """
    db_ad = service.update_ad(db=db, ad_id=ad_id, ad_update=ad_update)
    if db_ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")
    return db_ad


# ===========================
# DELETE - COM AUTENTICAÇÃO
# ===========================
@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Deleta ad por ID (requer autenticação de admin)
    """
    deleted = service.delete_ad(db=db, ad_id=ad_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ad not found")
    return None
