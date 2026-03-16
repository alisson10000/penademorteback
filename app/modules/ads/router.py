from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import shutil
from pathlib import Path
import re
import os

from app.core.database import get_db
from app.modules.admin.dependencies import get_current_admin

from . import schemas, service

router = APIRouter(tags=["Ads"])

STATIC_DIR = Path(os.getenv("STATIC_DIR", "/opt/penademorteback/static"))


@router.get("/", response_model=List[schemas.Ad])
def read_ads(
    skip: int = 0,
    limit: int = 100,
    ativo_only: bool = True,
    db: Session = Depends(get_db),
):

    ads = service.get_ads(db, skip=skip, limit=limit, ativo_only=ativo_only)

    return ads


@router.get("/random", response_model=schemas.Ad)
def read_random_ad(db: Session = Depends(get_db)):

    ad = service.get_random_active_ad(db)

    if ad is None:
        raise HTTPException(status_code=404, detail="No active ads")

    return ad


@router.get("/{ad_id}", response_model=schemas.Ad)
def read_ad(ad_id: int, db: Session = Depends(get_db)):

    ad = service.get_ad(db, ad_id=ad_id)

    if ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")

    return ad


@router.post("/", response_model=schemas.Ad, status_code=status.HTTP_201_CREATED)
def create_ad(
    ad_in: schemas.AdCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):

    return service.create_ad(
        db=db,
        ad=ad_in,
        created_by_id=current_admin.id,
    )


@router.put("/{ad_id}", response_model=schemas.Ad)
def update_ad(
    ad_id: int,
    ad_update: schemas.AdUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):

    db_ad = service.update_ad(db=db, ad_id=ad_id, ad_update=ad_update)

    if db_ad is None:
        raise HTTPException(status_code=404, detail="Ad not found")

    return db_ad


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad(
    ad_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):

    deleted = service.delete_ad(db=db, ad_id=ad_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Ad not found")

    return None


@router.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    current_admin=Depends(get_current_admin),
):

    if not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="Arquivo deve ser um vídeo",
        )

    videos_dir = STATIC_DIR / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    filename = file.filename.replace(" ", "_")
    filename = re.sub(r"[^a-zA-Z0-9._-]", "", filename)

    file_path = videos_dir / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "url": f"/static/videos/{filename}",
        "filename": filename,
        "size": file_path.stat().st_size,
        "content_type": file.content_type,
    }


@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    current_admin=Depends(get_current_admin),
):

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Arquivo deve ser uma imagem",
        )

    images_dir = STATIC_DIR / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    filename = file.filename.replace(" ", "_")
    filename = re.sub(r"[^a-zA-Z0-9._-]", "", filename)

    file_path = images_dir / filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "url": f"/static/images/{filename}",
        "filename": filename,
        "size": file_path.stat().st_size,
        "content_type": file.content_type,
    }