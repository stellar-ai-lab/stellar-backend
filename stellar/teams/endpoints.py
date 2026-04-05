from fastapi import APIRouter, Depends, Request, status

from stellar.dependencies import AuthDependency, get_team_service
from stellar.rate_limiter import limiter
from stellar.teams.schemas import TeamCreation, TeamResponse
from stellar.teams.service import TeamService

router = APIRouter(prefix="/teams", tags=["Teams Service Endpoints"])


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
