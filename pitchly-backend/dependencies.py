# Responsibility: shared FastAPI dependencies injected into route functions
# get_current_user enforces authentication on every protected endpoint

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client

from app.config import get_settings

logger = logging.getLogger(__name__)
security = HTTPBearer()
settings = get_settings()

_supabase = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key,
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Verify JWT on every protected request.
    Always extracts user from Supabase Auth — never trusts user_id from body.
    """
    token = credentials.credentials
    try:
        response = _supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return response.user
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Auth verification failed: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )