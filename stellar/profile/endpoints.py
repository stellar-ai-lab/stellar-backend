from fastapi import APIRouter, Depends, Request, status

from stellar.dependencies import AuthDependency, get_profile_service
from stellar.profile.schemas import CreateProfile, Profile, PublicProfile
from stellar.profile.service import ProfileService
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/profile", tags=["Profile Service Endpoints"])


@router.get("/", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_profile(
    request: Request,
    auth: AuthDependency,
    service: ProfileService = Depends(get_profile_service),
) -> Profile:
    """Get current user profile."""
    return await service.get_profile(auth.current_user_id, auth.client)


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_profile_by_user_id(
    request: Request,
    user_id: str,
    auth: AuthDependency,
    service: ProfileService = Depends(get_profile_service),
) -> PublicProfile:
    """Get profile by user ID."""
    return await service.get_profile_by_user_id(user_id, auth.client)


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
async def create_profile(
    request: Request,
    payload: CreateProfile,
    auth: AuthDependency,
    service: ProfileService = Depends(get_profile_service),
) -> Profile:
    """Create a new profile."""
    return await service.create_profile(payload, auth.current_user_id, auth.client)


# @router.put("/", status_code=status.HTTP_200_OK)
# @limiter.limit("5/minute")
# async def update_profile(
#     request: Request,
#     payload: UpdateProfile,
#     auth: AuthDependency,
#     service: ProfileService = Depends(get_profile_service),
# ) -> Profile:
#     """Update a profile."""
#     return await service.update_profile(payload, auth.current_user_id, auth.client)
