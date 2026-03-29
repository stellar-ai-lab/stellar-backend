import logging

from fastapi import HTTPException, status
from postgrest.exceptions import APIError
from supabase import AsyncClient

from stellar.profile.schemas import CreateProfile, Profile, UpdateProfile

log = logging.getLogger(__name__)


class ProfileService:
    """Profile service."""

    TABLE_NAME = "profiles"

    async def get_profile(self, user_id: str, supabase: AsyncClient) -> Profile:
        """Get Current User Profile.

        Args:
            user_id: Current user ID.
            supabase: Supabase client.

        Returns:
            Current user profile.
        """
        try:
            response = (
                await supabase.table(self.TABLE_NAME)
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found",
                )

            return Profile(**response.data[0])
        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to get profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get profile",
            )
        except Exception as e:
            log.exception(f"Failed to get profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from None

    async def create_profile(
        self,
        payload: CreateProfile,
        user_id: str,
        supabase: AsyncClient,
    ) -> Profile:
        """Create a new profile.

        Args:
            payload: Payload to create a new profile.
            user_id: Current user ID.
            supabase: Supabase client.

        Returns:
            Created profile.
        """
        try:
            # check if profile already exists
            check_profile = (
                await supabase.table(self.TABLE_NAME)
                .select("*")
                .eq("user_id", user_id)
                .execute()
            )
            if check_profile.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Profile already exists",
                )

            # create profile
            data = payload.model_dump(mode="json")
            data["user_id"] = user_id

            response = await supabase.table(self.TABLE_NAME).insert(data).execute()
            if not response.data or not response.data[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create profile",
                )

            return Profile(**response.data[0])
        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to create profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create profile",
            )
        except Exception as e:
            log.exception(f"Failed to create profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from None

    async def update_profile(
        self,
        payload: UpdateProfile,
        user_id: str,
        supabase: AsyncClient,
    ) -> Profile:
        """Update a profile.

        Args:
            payload: Payload to update a profile.
            user_id: Current user ID.
            supabase: Supabase client.

        Returns:
            Updated profile.
        """
        return Profile


profile_service = ProfileService()
