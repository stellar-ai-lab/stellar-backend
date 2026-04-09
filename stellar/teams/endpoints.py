from typing import List

from fastapi import APIRouter, Depends, Request, status

from stellar.dependencies import AuthDependency, get_team_service
from stellar.rate_limiter import limiter
from stellar.teams.schemas import (
    TeamCreation,
    TeamMemberCreation,
    TeamMemberResponse,
    TeamResponse,
)
from stellar.teams.service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams Endpoints"])


@router.get("/", status_code=status.HTTP_200_OK)
@limiter.limit("15/minute")
async def get_all_teams(
    request: Request,
    auth: AuthDependency,
    service: TeamService = Depends(get_team_service),
) -> List[TeamResponse]:
    """Get the list of all teams."""
    return await service.get_all_teams(auth)


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_team(
    request: Request,
    payload: TeamCreation,
    auth: AuthDependency,
    service: TeamService = Depends(get_team_service),
) -> TeamResponse:
    """Create a new team."""
    return await service.create_team(payload, auth)


@router.post("/{team_id}/members", status_code=status.HTTP_201_CREATED)
@limiter.limit("15/minute")
async def add_team_member(
    request: Request,
    team_id: str,
    payload: TeamMemberCreation,
    auth: AuthDependency,
    service: TeamService = Depends(get_team_service),
) -> TeamMemberResponse:
    """Add a new member to a team."""
    return await service.add_team_member(team_id, payload, auth)


@router.get("/{team_id}", status_code=status.HTTP_200_OK)
@limiter.limit("15/minute")
async def get_team_members_by_team_id(
    request: Request,
    team_id: str,
    auth: AuthDependency,
    service: TeamService = Depends(get_team_service),
) -> List[TeamMemberResponse]:
    """Get the list of members of a team."""
    return await service.get_team_members_by_team_id(team_id, auth)
