import logging

from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from supabase import AsyncClient
from supabase_auth.errors import AuthApiError

from stellar.account.schemas import (
    CreateUserAccount,
    CreateUserAccountResponse,
    LoginRequest,
    LoginResponse,
)
from stellar.enums import AccountStatus, AllowedCreationRoles

log = logging.getLogger(__name__)


class AccountService:
    """Account service."""

    # FOR TESTING ONLY
    async def login(
        self,
        payload: LoginRequest,
        supabase: AsyncClient,
    ) -> LoginResponse:
        """Login user."""
        try:
            login = await supabase.auth.sign_in_with_password(
                {"email": payload.email, "password": payload.password}
            )
            if not login.session or not login.session.access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to login",
                )

            return LoginResponse(
                access_token=login.session.access_token,
                refresh_token=login.session.refresh_token,
            )
        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to login: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to login",
            )
        except Exception as e:
            log.exception(f"Failed to login: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from None

    async def create_user_account(
        self,
        payload: CreateUserAccount,
        token: str,
        supabase: AsyncClient,
    ) -> CreateUserAccountResponse:
        """Create a new user account.

        Args:
            payload: Payload to create a new user account.
            token: Current user token.
            supabase: Supabase client.

        Returns:
            Created account.
        """
        try:
            check_user = await supabase.auth.get_user(token)
            if not check_user or not check_user.user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User account not found",
                )

            user_role = check_user.user.user_metadata.get("role")
            if not self._is_allowed_role(user_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have the right role to create an account for other users",
                )

            # Use the admin API instead of sign_up — avoids confirmation emails
            # and their rate limits, marks the account as confirmed immediately,
            # and raises a proper AuthApiError on duplicate emails.
            new_account = await supabase.auth.admin.create_user(
                {
                    "email": payload.email,
                    "password": payload.password,
                    "email_confirm": True,
                    "user_metadata": {
                        "role": payload.role,
                        "status": AccountStatus.ACTIVE,
                    },
                }
            )
            if not new_account.user or not new_account.user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account",
                )

            return CreateUserAccountResponse(
                id=new_account.user.id,
                email=new_account.user.email,
                role=new_account.user.user_metadata.get("role", payload.role),
            )

        except HTTPException:
            raise
        except AuthApiError as e:
            log.warning(f"Auth error during account creation: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        except APIError as e:
            log.exception(f"Failed to create user account: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account",
            )
        except Exception as e:
            log.exception(f"Failed to create user account: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from None

    def _is_allowed_role(self, role: str | None) -> bool:
        """Check if the role is allowed to create an account for other users.

        Args:
            role: The role to check.

        Returns:
            True if the role is allowed to create an account for other users, False otherwise.
        """
        if role is None:
            return False

        try:
            AllowedCreationRoles(role)
            return True
        except ValueError:
            return False


account_service = AccountService()
