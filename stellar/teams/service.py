import logging

from fastapi import HTTPException, status
from postgrest.exceptions import APIError

from stellar.auth_context import AuthContext
from stellar.enums import AllowedCreationRoles
from stellar.teams.schemas import (
    TeamCreation,
    TeamMemberCreation,
    TeamMemberResponse,
    TeamResponse,
)

log = logging.getLogger(__name__)


class TeamService:
    """Team service."""

    TEAMS_TABLE = "teams"
    TEAMS_MEMBERS_TABLE = "team_members"

    async def create_team(
        self, payload: TeamCreation, auth: AuthContext
    ) -> TeamResponse:
        """Create a new team.

        Args:
            payload: Payload to create a new team.
            auth: Authentication context.

        Returns:
            Created team response.
        """
        supabase = auth.client
        current_user_id = auth.current_user_id

        try:
            if not self._can_create_team(auth.role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission to create teams",
                )

            existing = (
                await supabase.table(self.TEAMS_TABLE)
                .select("id")
                .eq("name", payload.name)
                .execute()
            )
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Team already exists",
                )

            data = payload.model_dump(mode="json")
            data["created_by"] = current_user_id
            data["is_active"] = True

            response = await supabase.table(self.TEAMS_TABLE).insert(data).execute()
            if not response.data or not response.data[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create team",
                )

            return TeamResponse(**response.data[0])
        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to create team: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create team",
            )
        except Exception as e:
            log.exception(f"Failed to create team: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from None

    def _can_create_team(self, role: str | None) -> bool:
        """Return True if the role may create teams."""

        if role is None:
            return False
        try:
            AllowedCreationRoles(role)
            return True
        except ValueError:
            return False

    async def add_team_member(
        self, team_id: str, payload: TeamMemberCreation, auth: AuthContext
    ) -> TeamMemberResponse:
        """Add a new member to a team.

        Args:
            team_id: Team ID.
            payload: Payload to add a new member to a team.
            auth: Authentication context.

        Returns:
            Added team member response.
        """
        supabase = auth.client
        current_user_name = auth.current_user_name

        try:
            if not self._can_add_team_member(auth.role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have permission to add team members",
                )

            check_team = (
                await supabase.table(self.TEAMS_TABLE)
                .select("id, is_active")
                .eq("id", team_id)
                .execute()
            )
            if not check_team.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Team not found",
                )

            if not check_team.data[0]["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Team is not active",
                )

            check_member = (
                await supabase.table(self.TEAMS_MEMBERS_TABLE)
                .select("id")
                .eq("team_id", team_id)
                .eq("user_id", payload.user_id)
                .execute()
            )
            if check_member.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Member already exists",
                )

            data = payload.model_dump(mode="json")
            data["team_id"] = team_id
            data["added_by"] = current_user_name

            response = (
                await supabase.table(self.TEAMS_MEMBERS_TABLE).insert(data).execute()
            )
            if not response.data or not response.data[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to add team member",
                )

            return TeamMemberResponse(**response.data[0])
        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to add team member: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to add team member",
            )
        except Exception as e:
            log.exception(f"Failed to add team member: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from None


team_service = TeamService()
