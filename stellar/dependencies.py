import logging
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import AsyncClient, AsyncClientOptions, acreate_client

from stellar.account.service import AccountService, account_service
from stellar.config import settings

security = HTTPBearer()

log = logging.getLogger(__name__)


@dataclass
class AuthContext:
    client: AsyncClient
    current_user_id: str
    token: str


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthContext:
    """Get the supabase and auth context"""
    try:
        token = credentials.credentials

        supabase_client = await acreate_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SECRET_KEY,
            options=AsyncClientOptions(
                headers={"Authorization": f"Bearer {token}"}
            ),  # allow to access the supabase bucket
        )

        response = await supabase_client.auth.get_user(token)
        if not response or not response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )

        return AuthContext(
            client=supabase_client,
            current_user_id=response.user.id,
            token=token,
        )
    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Failed to get auth context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


AuthDependency = Annotated[AuthContext, Depends(get_auth_context)]


def get_account_service() -> AccountService:
    """Return the shared account service instance."""
    return account_service
