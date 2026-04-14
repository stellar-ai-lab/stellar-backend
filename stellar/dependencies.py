import logging
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import AsyncClientOptions, AuthApiError, acreate_client

from stellar.account.service import AccountService, account_service
from stellar.attendance.service import AttendanceService, attendance_service
from stellar.auth_context import AuthContext
from stellar.config import settings
from stellar.dev.service import DevService, dev_service
from stellar.profile.service import ProfileService, profile_service
from stellar.teams.service import TeamService, team_service

security = HTTPBearer()

log = logging.getLogger(__name__)


async def get_auth_context(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> AuthContext:
    """Get the supabase and auth context"""
    try:
        token = credentials.credentials

        supabase_client = await acreate_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_ANON_KEY,
            options=AsyncClientOptions(headers={"Authorization": f"Bearer {token}"}),
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
            role=response.user.user_metadata.get("role"),
        )

    except HTTPException:
        raise
    except AuthApiError as e:
        log.warning(f"Auth error during get auth context: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    except Exception as e:
        log.exception(f"Failed to get auth context: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from None


AuthDependency = Annotated[AuthContext, Depends(get_auth_context)]


def get_dev_service() -> DevService:
    """Return the shared dev service instance."""
    return dev_service


def get_account_service() -> AccountService:
    """Return the shared account service instance."""
    return account_service


def get_profile_service() -> ProfileService:
    """Return the shared profile service instance."""
    return profile_service


def get_team_service() -> TeamService:
    """Return the shared team service instance."""
    return team_service


def get_attendance_service() -> AttendanceService:
    """Return the shared attendance service instance."""
    return attendance_service
