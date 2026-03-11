from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
import secrets
import smtplib
from email.message import EmailMessage  # Python 3.12 ✅

from fastapi import HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import (
    ADMIN_JWT_SECRET,
    ADMIN_JWT_ALG,
    ADMIN_JWT_EXPIRE_MIN,
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_HOST,
    MAIL_PORT,
    FRONTEND_URL,  # ← ADICIONADO
)
from app.modules.admin.models import Admin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =========================
# 🔒 Helpers (bcrypt safety)
# =========================
def _ensure_bcrypt_len(password: str) -> None:
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha muito longa. Máximo: 72 bytes (evite emojis).",
        )

def hash_password(password: str) -> str:
    _ensure_bcrypt_len(password)
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    _ensure_bcrypt_len(password)
    return pwd_context.verify(password, password_hash)

# =========================
# 📧 EMAIL SENDER
# =========================
def send_reset_email(email: str, reset_token: str, reset_url: str) -> None:
    """Envia email com link de reset - Python 3.12"""
    reset_link = f"{reset_url}?token={reset_token}"
    
    body_html = f"""
    <html>
        <body style='font-family: Arial, sans-serif; max-width: 600px;'>
            <h2 style='color: #007bff;'>🔑 Recuperação de Senha - PenadeMorte Admin</h2>
            <p>Você solicitou recuperação de senha para <strong>{email}</strong>.</p>
            <p><strong>Link válido por 15 minutos:</strong></p>
            <div style='background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #007bff;'>
                <a href="{reset_link}" style='color: #007bff; text-decoration: none; font-family: monospace;'>{reset_link}</a>
            </div>
            <p style='color: #666; font-size: 14px;'>
                <small>Se não solicitou este reset, ignore este email.</small>
            </p>
        </body>
    </html>
    """
    
    msg = EmailMessage()
    msg['Subject'] = "🔑 Recuperação de Senha - PenadeMorte"
    msg['From'] = MAIL_USERNAME
    msg['To'] = email
    msg.set_content(body_html, subtype='html')
    
    try:
        server = smtplib.SMTP(MAIL_HOST, MAIL_PORT)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email enviado para {email}")
    except Exception as e:
        print(f"❌ Email falhou: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Falha no email: {str(e)}"
        )

# =========================
# ✅ Auth
# =========================
def authenticate_admin(db: Session, email: str, password: str) -> Optional[Admin]:
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or not admin.is_active:
        return None
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
        if not sub or not isinstance(int(sub), int):
            raise cred_exc
        return payload
    except JWTError:
        raise cred_exc

# =========================
# 🔄 PASSWORD RESET
# =========================
def request_password_reset(db: Session, email: str) -> str:
    """Gera token e envia email de reset"""
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or not admin.is_active:
        return "Se email cadastrado, verifique sua caixa de entrada."

    reset_token = secrets.token_hex(32)
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    
    admin.reset_token = reset_token
    admin.reset_token_expires_at = expires_at
    db.add(admin)
    db.commit()
    
    reset_url = f"{FRONTEND_URL}/reset-password"
    send_reset_email(email, reset_token, reset_url)
    
    return "Email de recuperação enviado. Verifique sua caixa de entrada (válido por 15min)."

def confirm_password_reset(db: Session, token: str, new_password: str) -> str:
    """Valida token e atualiza senha"""
    admin = db.query(Admin).filter(
        Admin.reset_token == token,
        Admin.reset_token_expires_at > datetime.utcnow(),
        Admin.is_active == True
    ).first()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou expirado."
        )
    
    admin.password_hash = hash_password(new_password)
    admin.reset_token = None
    admin.reset_token_expires_at = None
    
    db.add(admin)
    db.commit()
    
    return "Senha atualizada com sucesso!"

# =========================
# ✅ Admin CRUD
# =========================
def get_admin_by_id(db: Session, admin_id: int) -> Optional[Admin]:
    return db.query(Admin).filter(Admin.id == admin_id).first()

def admin_count(db: Session) -> int:
    return db.query(Admin).count()

def create_admin(db: Session, email: str, password: str, role: str = "admin", is_active: bool = True) -> Admin:
    email_norm = email.strip().lower()
    exists = db.query(Admin).filter(Admin.email == email_norm).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="E-mail já cadastrado.")
    
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
    if admin_count(db) > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cadastro bloqueado. Apenas superadmin pode criar novos administradores.",
        )
    return create_admin(db, email=email, password=password, role="superadmin", is_active=True)

def create_admin_by_superadmin(
    db: Session, current_admin: Admin, email: str, password: str, 
    role: str = "admin", is_active: bool = True
) -> Admin:
    if current_admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas superadmin pode criar administradores.",
        )
    return create_admin(db, email=email, password=password, role=role, is_active=is_active)
