from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil
from pathlib import Path

from app.core.database import get_db
from app.modules.admin.dependencies import get_current_admin
from . import schemas, service

router = APIRouter(tags=["Ads"])


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


# ===========================
# UPLOAD - COM AUTENTICAÇÃO
# ===========================
@router.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    current_admin=Depends(get_current_admin),
):
    """
    Upload de vídeo MP4 para /static/videos/
    Retorna a URL pública do vídeo
    """
    # Valida tipo de arquivo
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="Arquivo deve ser um vídeo (MP4, MOV, etc.)"
        )
    
    # Caminho onde salvar
    static_dir = Path(__file__).parent.parent.parent / "static" / "videos"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo (sanitiza para evitar problemas)
    filename = file.filename.replace(" ", "_")
    file_path = static_dir / filename
    
    # Salvar arquivo
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )
    
    # URL pública
    url = f"/static/videos/{filename}"
    
    return {
        "url": url,
        "filename": filename,
        "size": file_path.stat().st_size,
        "content_type": file.content_type,
    }


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_admin=Depends(get_current_admin),
):
    """
    Upload de imagem para /static/images/
    Retorna a URL pública da imagem
    """
    # Valida tipo de arquivo
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Arquivo deve ser uma imagem (JPG, PNG, etc.)"
        )
    
    # Caminho onde salvar
    static_dir = Path(__file__).parent.parent.parent / "static" / "images"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo
    filename = file.filename.replace(" ", "_")
    file_path = static_dir / filename
    
    # Salvar arquivo
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar arquivo: {str(e)}"
        )
    
    # URL pública
    url = f"/static/images/{filename}"
    
    return {
        "url": url,
        "filename": filename,
        "size": file_path.stat().st_size,
        "content_type": file.content_type,
    }
