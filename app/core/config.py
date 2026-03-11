import os
from dotenv import load_dotenv
from typing import Optional


load_dotenv()


# ===========================
# DATABASE
# ===========================
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não configurada no .env")


# ===========================
# ADMIN AUTH (JWT)
# ===========================
ADMIN_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET")
if not ADMIN_JWT_SECRET or len(ADMIN_JWT_SECRET) < 32:
    raise ValueError("ADMIN_JWT_SECRET deve ter pelo menos 32 caracteres")

ADMIN_JWT_ALG = os.getenv("ADMIN_JWT_ALG", "HS256")
ADMIN_JWT_EXPIRE_MIN = int(os.getenv("ADMIN_JWT_EXPIRE_MIN", "60"))


# ===========================
# EMAIL (SMTP)
# ===========================
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_HOST = os.getenv("MAIL_HOST", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))

# Validação obrigatória para reset funcionar
if not MAIL_USERNAME or not MAIL_PASSWORD:
    raise ValueError("MAIL_USERNAME e MAIL_PASSWORD são obrigatórios para recuperação de senha")


# ===========================
# FRONTEND URL (para links de reset)
# ===========================
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
