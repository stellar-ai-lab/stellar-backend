import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import AsyncClient, acreate_client

from stellar.account.service import AccountService, account_service
from stellar.config import settings

security = HTTPBearer()

log = logging.getLogger(__name__)


async def get_supabase_client() -> AsyncClient:
    """Get the supabase client."""
    return await acreate_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SECRET_KEY,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    supabase: AsyncClient = Depends(get_supabase_client),
) -> str:
    """Get the current user id from the Bearer token via Supabase."""
    token = credentials.credentials
    try:
        response = await supabase.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )
        return response.user.id
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Failed to resolve current user from Supabase: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Get the current user token from the Bearer token."""
    return credentials.credentials


def get_account_service() -> AccountService:
    """Return the shared account service instance."""
    return account_service
