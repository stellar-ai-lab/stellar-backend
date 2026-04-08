import logging

from fastapi import HTTPException, status
from postgrest import APIError

from stellar.auth_context import AuthContext
from stellar.profile.schemas import ProfileCreation, ProfileResponse

log = logging.getLogger(__name__)


class ProfileService:
    """Profile service."""

    PROFILES_TABLE = "profiles"

    async def create_user_profile(
        self, payload: ProfileCreation, auth: AuthContext
    ) -> ProfileResponse:
        """Create a new user profile.

        Args:
            payload: Payload to create a new user profile.
            auth: Authentication context.

        Returns:
            Created user profile.
        """
        supabase = auth.client
        current_user_id = auth.current_user_id
        try:
            existing = (
                await supabase.table(self.PROFILES_TABLE)
                .select("user_id")
                .eq("user_id", current_user_id)
                .execute()
            )
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Profile already exists",
                )

            data = payload.model_dump(mode="json")
            data["user_id"] = current_user_id

            response = await supabase.table(self.PROFILES_TABLE).insert(data).execute()
            if not response.data or not response.data[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user profile",
                )

            return ProfileResponse(**response.data[0])
        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to create user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user profile",
            )
        except Exception as e:
            log.exception(f"Failed to create user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from None

    # async def get_profile(self, user_id: str, supabase: AsyncClient) -> Profile:
    #     """Get current user profile.

    #     Args:
    #         user_id: Current user ID.
    #         supabase: Supabase client.

    #     Returns:
    #         Current user profile.
    #     """
    #     try:
    #         response = (
    #             await supabase.table(self.TABLE_NAME)
    #             .select("*")
    #             .eq("user_id", user_id)
    #             .execute()
    #         )
    #         if not response.data:
    #             raise HTTPException(
    #                 status_code=status.HTTP_404_NOT_FOUND,
    #                 detail="Profile not found",
    #             )

    #         return Profile(**response.data[0])
    #     except HTTPException:
    #         raise
    #     except APIError as e:
    #         log.exception(f"Failed to get profile: {e}")
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Failed to get profile",
    #         )
    #     except Exception as e:
    #         log.exception(f"Failed to get profile: {e}")
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail="Internal server error",
    #         ) from None

    # async def get_profile_by_user_id(
    #     self, user_id: str, supabase: AsyncClient
    # ) -> PublicProfile:
    #     """Get profile by user ID.

    #     Args:
    #         user_id: User ID.
    #         supabase: Supabase client.

    #     Returns:
    #         Profile by user ID.
    #     """
    #     try:
    #         response = (
    #             await supabase.table(self.TABLE_NAME)
    #             .select("*")
    #             .eq("user_id", user_id)
    #             .execute()
    #         )
    #         if not response.data:
    #             raise HTTPException(
    #                 status_code=status.HTTP_404_NOT_FOUND,
    #                 detail="Profile not found",
    #             )

    #         return PublicProfile(**response.data[0])
    #     except HTTPException:
    #         raise
    #     except APIError as e:
    #         log.exception(f"Failed to get profile by user ID: {e}")
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Failed to fetch the profile",
    #         )
    #     except Exception as e:
    #         log.exception(f"Failed to get profile by user ID: {e}")
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail="Internal server error",
    #         ) from None

    # async def update_profile(
    #     self,
    #     payload: UpdateProfile,
    #     user_id: str,
    #     supabase: AsyncClient,
    # ) -> Profile:
    #     """Update a profile.

    #     Args:
    #         payload: Payload to update a profile.
    #         user_id: Current user ID.
    #         supabase: Supabase client.

    #     Returns:
    #         Updated profile.
    #     """
    #     try:
    #         # check if profile exists
    #         check_profile = (
    #             await supabase.table(self.TABLE_NAME)
    #             .select("*")
    #             .eq("user_id", user_id)
    #             .execute()
    #         )
    #         if not check_profile.data:
    #             raise HTTPException(
    #                 status_code=status.HTTP_404_NOT_FOUND,
    #                 detail="Profile not found",
    #             )

    #         # update profile
    #         data = payload.model_dump(mode="json", exclude_none=True)
    #         if not data:
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail="No data to update",
    #             )

    #         response = (
    #             await supabase.table(self.TABLE_NAME)
    #             .update(data)
    #             .eq("user_id", user_id)
    #             .execute()
    #         )

    #         if not response.data:
    #             raise HTTPException(
    #                 status_code=status.HTTP_400_BAD_REQUEST,
    #                 detail="Failed to update profile",
    #             )

    #         return Profile(**response.data[0])
    #     except HTTPException:
    #         raise
    #     except APIError as e:
    #         log.exception(f"Failed to update profile: {e}")
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Failed to update profile",
    #         )
    #     except Exception as e:
    #         log.exception(f"Failed to update profile: {e}")
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail="Internal server error",
    #         ) from None


profile_service = ProfileService()
