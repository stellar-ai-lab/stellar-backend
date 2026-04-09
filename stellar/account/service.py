import logging

from fastapi import HTTPException, status
from postgrest import APIError
from supabase import AuthApiError, acreate_client

from stellar.account.schemas import AccountCreation, AccountResponse
from stellar.auth_context import AuthContext
from stellar.config import settings
from stellar.enums import AdminRole

log = logging.getLogger(__name__)


class AccountService:
    """Account service."""

    async def create_user_account(
        self, payload: AccountCreation, auth: AuthContext
    ) -> AccountResponse:
        """Create a new user account.

        Args:
            payload: Payload to create a new user account.
            auth: Authentication context.

        Returns:
            Created user account.
        """
        user_role = auth.role
        current_user_id = auth.current_user_id
        try:
            if not self._is_allowed_role(user_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have the right role to create an account for other users",
                )

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
                        "created_by": current_user_id,
                    },
                }
            )
            if not new_account.user or not new_account.user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account",
                )

            metadata = new_account.user.user_metadata
            return AccountResponse(
                id=new_account.user.id,
                email=new_account.user.email,
                role=metadata.get("role"),
                created_by=metadata.get("created_by"),
                created_at=new_account.user.created_at,
                updated_at=new_account.user.updated_at,
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
            )

    def _is_allowed_role(self, role: str | None) -> bool:
        """Check if the role is allowed to perform the action.

        Args:
            role: The role to check.

        Returns:
            True if the role is allowed to perform the action, False otherwise.
        """
        if role is None:
            return False

        try:
            AdminRole(role)
            return True
        except ValueError:
            return False


account_service = AccountService()
