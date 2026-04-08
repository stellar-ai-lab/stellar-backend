from fastapi import APIRouter, Depends, Request, status

from stellar.dependencies import AuthDependency, get_profile_service
from stellar.profile.schemas import (
    ProfileCreation,
    ProfileResponse,
)
from stellar.profile.service import ProfileService
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/profile", tags=["Profile Service Endpoints"])


@router.get("/", status_code=status.HTTP_200_OK)
@limiter.limit("15/minute")
async def get_current_user_profile(
    request: Request,
    auth: AuthDependency,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Get the current user profile."""
    return await service.get_current_user_profile(auth)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
@limiter.limit("15/minute")
async def get_user_profile_by_user_id(
    request: Request,
    user_id: str,
    auth: AuthDependency,
    service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Get a user profile by user ID."""
    return await service.get_user_profile_by_user_id(user_id, auth)


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
