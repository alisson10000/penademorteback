from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import (
    ADMIN_JWT_SECRET,
    ADMIN_JWT_ALG,
    ADMIN_JWT_EXPIRE_MIN,
)
from app.modules.admin.models import Admin


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# 🔒 Helpers (bcrypt safety)
# =========================
def _ensure_bcrypt_len(password: str) -> None:
    # bcrypt suporta no máximo 72 BYTES (não caracteres)
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha muito longa. Máximo permitido: 72 bytes (evite emojis).",
        )


def hash_password(password: str) -> str:
    _ensure_bcrypt_len(password)
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    _ensure_bcrypt_len(password)
    return pwd_context.verify(password, password_hash)


# =========================
# ✅ Auth
# =========================
def authenticate_admin(db: Session, email: str, password: str) -> Optional[Admin]:
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or not admin.is_active:
        return None

    # se senha for inválida/errada, retorna None (login falha)
    if not verify_password(password, admin.password_hash):
        return None

    return admin


def touch_last_login(db: Session, admin: Admin) -> None:
    admin.last_login = datetime.utcnow()
    db.add(admin)
    db.commit()
    db.refresh(admin)


def create_admin_token(admin: Admin) -> str:
    now = datetime.utcnow()

    payload = {
        "sub": str(admin.id),
        "typ": "admin",
        "role": admin.role,
        # timestamps em int (mais compatível)
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ADMIN_JWT_EXPIRE_MIN)).timestamp()),
    }

    return jwt.encode(payload, ADMIN_JWT_SECRET, algorithm=ADMIN_JWT_ALG)


def decode_admin_token(token: str) -> dict:
    cred_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, ADMIN_JWT_SECRET, algorithms=[ADMIN_JWT_ALG])

        if payload.get("typ") != "admin":
            raise cred_exc

        sub = payload.get("sub")
        if not sub:
            raise cred_exc

        # garante que sub é numérico (evita quebrar no int())
        try:
            int(sub)
        except Exception:
            raise cred_exc

        return payload
    except JWTError:
        raise cred_exc


# =========================
# ✅ Admin CRUD helpers
# =========================
def get_admin_by_id(db: Session, admin_id: int) -> Optional[Admin]:
    return db.query(Admin).filter(Admin.id == admin_id).first()


def admin_count(db: Session) -> int:
    return db.query(Admin).count()


def create_admin(
    db: Session,
    email: str,
    password: str,
    role: str = "admin",
    is_active: bool = True,
) -> Admin:
    # normaliza email (evita duplicidade por maiúscula/minúscula)
    email_norm = email.strip().lower()

    exists = db.query(Admin).filter(Admin.email == email_norm).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado.",
        )

    admin = Admin(
        email=email_norm,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def create_first_admin_if_allowed(db: Session, email: str, password: str) -> Admin:
    """
    Bootstrap seguro:
    - Se NÃO existir nenhum admin no banco, cria o primeiro como superadmin.
    - Se já existir, bloqueia (cadastro deve ser feito por superadmin autenticado).
    """
    if admin_count(db) > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cadastro bloqueado. Apenas superadmin pode criar novos administradores.",
        )

    # ignora role vindo do client, força superadmin no primeiro
    return create_admin(db, email=email, password=password, role="superadmin", is_active=True)


def create_admin_by_superadmin(
    db: Session,
    current_admin: Admin,
    email: str,
    password: str,
    role: str = "admin",
    is_active: bool = True,
) -> Admin:
    if current_admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas superadmin pode criar administradores.",
        )

    # se quiser travar para nunca permitir criar superadmin via API, descomente:
    # if role == "superadmin":
    #     raise HTTPException(status_code=403, detail="Não é permitido criar superadmin por esta rota.")

    return create_admin(db, email=email, password=password, role=role, is_active=is_active)