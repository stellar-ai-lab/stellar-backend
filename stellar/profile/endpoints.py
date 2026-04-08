from fastapi import APIRouter, Depends, Request, status

from stellar.dependencies import AuthDependency, get_profile_service
from stellar.profile.schemas import (
    ProfileCreation,
    ProfileResponse,
)
from stellar.profile.service import ProfileService
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/profile", tags=["Profile Service Endpoints"])


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
async def create_user_profile(
    request: Request,
    payload: ProfileCreation,
    auth: AuthDependency,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Create a new user profile."""
    return await service.create_user_profile(payload, auth)
