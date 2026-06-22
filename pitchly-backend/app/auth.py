from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.supabase_client import get_supabase_admin

security = HTTPBearer(auto_error=False)


def get_user_id_from_authorization(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Expected Bearer token")

    try:
        response = get_supabase_admin().auth.get_user(token)
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid Supabase token") from exc

    user = getattr(response, "user", None)
    user_id = getattr(user, "id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid Supabase token")

    return user_id


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
):
    # Responsibility: Verify Supabase bearer tokens for protected endpoints.
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    try:
        response = get_supabase_admin().auth.get_user(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    user = getattr(response, "user", None)
    if not getattr(user, "id", None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return user
