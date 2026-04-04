from typing import List

from fastapi import APIRouter, Depends, Request, status
from supabase import AsyncClient

from stellar.account.schemas import (
    CreateUserAccountResponse,
    LoginRequest,
    UserAccountCreation,
    UserAccountResponse,
)
from stellar.account.service import AccountService
from stellar.dependencies import (
    AuthDependency,
    get_account_service,
    get_supabase_client,
)
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/account", tags=["Account Service Endpoints"])


# FOR LOCAL DEVELOPMENT TESTING ONLY
@router.post("/login")
async def login(
    request: Request,
    payload: LoginRequest,
    supabase: AsyncClient = Depends(get_supabase_client),
    service: AccountService = Depends(get_account_service),
):
    """Login user."""
    return await service.login(payload, supabase)


@router.get("/", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def get_user_accounts(
    request: Request,
    auth: AuthDependency,
    service: AccountService = Depends(get_account_service),
) -> List[UserAccountResponse]:
    """Get all user accounts."""
    return await service.get_user_accounts(auth)


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_user_account(
    request: Request,
    payload: UserAccountCreation,
    auth: AuthDependency,
    service: AccountService = Depends(get_account_service),
) -> CreateUserAccountResponse:
    """Create new user account."""
    return await service.create_user_account(payload, auth.token, auth.client)
