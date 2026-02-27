from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Literal


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

    # Pydantic v2
    model_config = ConfigDict(from_attributes=True)


# =========================
# ADMIN - CREATE (INPUT)
# =========================
class AdminCreateIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)

    # se você quiser travar os papéis aceitos, use Literal:
    # role: Literal["admin", "superadmin"] = "admin"
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