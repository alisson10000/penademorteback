from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.schemas import (
    AdminLoginIn,
    TokenOut,
    AdminOut,
    AdminCreateIn,
    AdminMeOut,
    PasswordResetRequestIn,
    PasswordResetConfirmIn,
    # PasswordResetTokenOut REMOVIDO (não usado)
)
from app.modules.admin.service import (
    authenticate_admin,
    create_admin_token,
    touch_last_login,
    create_first_admin_if_allowed,
    create_admin_by_superadmin,
    request_password_reset,
    confirm_password_reset,
)
from app.modules.admin.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


# ===========================
# AUTH - LOGIN (EXISTENTE ✅)
# ===========================
@router.post("/auth/login", response_model=TokenOut)
def admin_login(payload: AdminLoginIn, db: Session = Depends(get_db)):
    admin = authenticate_admin(db, payload.email, payload.password)
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    touch_last_login(db, admin)
    token = create_admin_token(admin)
    return TokenOut(access_token=token)


# ===========================
# AUTH - ME (EXISTENTE ✅)
# ===========================
@router.get("/me", response_model=AdminMeOut)
def admin_me(admin=Depends(get_current_admin)):
    return admin


# ===========================
# REGISTER - BOOTSTRAP (EXISTENTE ✅)
# ===========================
@router.post("/auth/register", response_model=AdminOut)
def admin_register(payload: AdminCreateIn, db: Session = Depends(get_db)):
    """
    Bootstrap:
    - Se ainda não existe nenhum admin: cria o 1º como superadmin (ignora role enviado).
    - Se já existe: bloqueia (use /admin/auth/register-by-admin com token de superadmin).
    """
    admin = create_first_admin_if_allowed(db, email=payload.email, password=payload.password)
    return admin


# ===========================
# REGISTER - SUPERADMIN (EXISTENTE ✅)
# ===========================
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


# ===========================
# 🔄 PASSWORD RESET - NOVOS ENDPOINTS ✅
# ===========================
@router.post("/auth/reset-password/request")
def reset_password_request(
    payload: PasswordResetRequestIn,
    db: Session = Depends(get_db)
):
    """
    POST /admin/auth/reset-password/request
    Envia email com link de reset (15min válido)
    """
    message = request_password_reset(db, payload.email)
    return {"message": message}


@router.post("/auth/reset-password/confirm")
def reset_password_confirm(
    payload: PasswordResetConfirmIn,
    db: Session = Depends(get_db)
):
    """
    POST /admin/auth/reset-password/confirm
    Confirma reset com token + nova senha
    """
    message = confirm_password_reset(db, payload.token, payload.password)
    return {"message": message}
