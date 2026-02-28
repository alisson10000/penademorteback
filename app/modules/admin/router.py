from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.schemas import (
    AdminLoginIn,
    TokenOut,
    AdminOut,
    AdminCreateIn,
    AdminMeOut,
)
from app.modules.admin.service import (
    authenticate_admin,
    create_admin_token,
    touch_last_login,
    create_first_admin_if_allowed,
    create_admin_by_superadmin,
)
from app.modules.admin.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post("/auth/login", response_model=TokenOut)
def admin_login(payload: AdminLoginIn, db: Session = Depends(get_db)):
    admin = authenticate_admin(db, payload.email, payload.password)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    touch_last_login(db, admin)
    token = create_admin_token(admin)
    return TokenOut(access_token=token)


@router.get("/me", response_model=AdminMeOut)
def admin_me(admin=Depends(get_current_admin)):
    return admin


@router.post("/auth/register", response_model=AdminOut)
def admin_register(payload: AdminCreateIn, db: Session = Depends(get_db)):
    """
    Bootstrap:
    - Se ainda não existe nenhum admin: cria o 1º como superadmin (ignora role enviado).
    - Se já existe: bloqueia (use /auth/register-by-admin com token de superadmin).
    """
    # Cria o primeiro admin SEM exigir token
    admin = create_first_admin_if_allowed(db, email=payload.email, password=payload.password)
    return admin


@router.post("/auth/register-by-admin", response_model=AdminOut)
def admin_register_by_admin(
    payload: AdminCreateIn,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Criação de admins APÓS bootstrap:
    - Exige token
    - Só superadmin pode criar
    """
    admin = create_admin_by_superadmin(
        db=db,
        current_admin=current_admin,
        email=payload.email,
        password=payload.password,
        role=payload.role,
        is_active=payload.is_active,
    )
    return admin