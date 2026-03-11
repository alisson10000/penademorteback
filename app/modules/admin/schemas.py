from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal
from datetime import datetime


# =========================
# AUTH - LOGIN
# =========================
class AdminLoginIn(BaseModel):
    email: EmailStr
    # bcrypt limita 72 BYTES; aqui limitamos por caracteres (ajuda muito).
    # No service você ainda pode validar por bytes pra garantir.
    password: str = Field(min_length=1, max_length=72)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


# =========================
# ADMIN - OUTPUT (FULL)
# =========================
class AdminOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    # Campos de reset (visíveis só se existirem)
    reset_token: str | None = None
    reset_token_expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# =========================
# ADMIN - CREATE (INPUT)
# =========================
class AdminCreateIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    role: str = Field(default="admin", min_length=3, max_length=50)
    is_active: bool = True


# =========================
# ADMIN - ME (OUTPUT MIN)
# =========================
class AdminMeOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)


# =========================
# PASSWORD RESET - INPUTS
# =========================
class PasswordResetRequestIn(BaseModel):
    """Para solicitar reset por email"""
    email: EmailStr


class PasswordResetConfirmIn(BaseModel):
    """Para confirmar reset com token + nova senha"""
    token: str = Field(min_length=32, max_length=255)
    password: str = Field(min_length=6, max_length=72)


