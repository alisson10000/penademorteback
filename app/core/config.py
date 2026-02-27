import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

ADMIN_JWT_SECRET = os.getenv("ADMIN_JWT_SECRET")
ADMIN_JWT_ALG = os.getenv("ADMIN_JWT_ALG", "HS256")
ADMIN_JWT_EXPIRE_MIN = int(os.getenv("ADMIN_JWT_EXPIRE_MIN", 60))