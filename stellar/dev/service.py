import logging

from fastapi import HTTPException, status
from postgrest import APIError
from supabase import AuthApiError, acreate_client

from stellar.config import settings
from stellar.dev.schemas import (
    LoginRequest,
    LoginResponse,
    TestAccountCreation,
    TestAccountResponse,
)

log = logging.getLogger(__name__)


class DevService:
    """Dev service."""

    async def create_test_account(self, payload: TestAccountCreation):
        """Create a new test account.

        Args:
            payload: Payload to create a new test account.

        Returns:
            Created test account.
        """
        try:
            admin_client = await acreate_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SECRET_KEY,
            )
            new_account = await admin_client.auth.admin.create_user(
                {
                    "email": payload.email,
                    "password": payload.password,
                    "email_confirm": True,
                    "user_metadata": {
                        "role": payload.role,
                        "created_by": payload.created_by,
                    },
                }
            )
            if not new_account.user or not new_account.user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account",
                )

            metadata = new_account.user.user_metadata
            return TestAccountResponse(
                id=new_account.user.id,
                email=new_account.user.email,
                role=metadata.get("role"),
                created_by=metadata.get("created_by"),
                created_at=new_account.user.created_at,
                updated_at=new_account.user.updated_at,
            )
        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Auth error during test account creation: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            log.exception(f"Failed to create test account: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def login_test_account(self, payload: LoginRequest):
        """Login test account.

        Args:
            payload: Payload to login test account.

        Returns:
            Logged in test account.
        """
        try:
            supabase = await acreate_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_ANON_KEY,
            )
            login = await supabase.auth.sign_in_with_password(
                {"email": payload.email, "password": payload.password}
            )
            if not login.session or not login.session.access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to login test account",
                )

            return LoginResponse(
                access_token=login.session.access_token,
                refresh_token=login.session.refresh_token,
            )
        except HTTPException:
            raise
        except AuthApiError as e:
            log.exception(f"Auth error during test account login: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except APIError as e:
            log.exception(f"Auth error during test account login: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except Exception as e:
            log.exception(f"Failed to login test account: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


dev_service = DevService()
