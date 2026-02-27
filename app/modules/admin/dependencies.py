from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.admin.service import decode_admin_token, get_admin_by_id
from app.modules.admin.models import Admin

security = HTTPBearer(auto_error=True)

def get_current_admin(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> Admin:
    token = creds.credentials
    payload = decode_admin_token(token)

    admin_id = int(payload["sub"])
    admin = get_admin_by_id(db, admin_id)

    if not admin or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return admin