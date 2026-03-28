import logging

from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from supabase import AsyncClient

from stellar.account.schemas import CreateUserAccount, CreateUserAccountResponse
from stellar.enums import AccountStatus, AllowedCreationRoles

log = logging.getLogger(__name__)


class AccountService:
    """Account service."""

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
            # verify that the user have the right role to create an account for other users
            check_role = await supabase.auth.get_user(token)
            if not check_role or not check_role.user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User account not found",
                )

            user_role = check_role.user.user_metadata.get("role")
            if not self._is_allowed_role(user_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have the right role to create an account for other users",
                )

            # create new account
            new_account = await supabase.auth.sign_up(
                {
                    "email": payload.email,
                    "password": payload.password,
                    "options": {
                        "data": {
                            "role": payload.role,
                            "status": AccountStatus.ACTIVE,
                        }
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

    def _is_allowed_role(role: str) -> bool:
        """Check if the role is allowed to create an account for other users.

        Args:
            role: The role to check.

        Returns:
            True if the role is allowed to create an account for other users, False otherwise.
        """
        try:
            AllowedCreationRoles(role)
            return True
        except ValueError:
            return False


account_service = AccountService()
