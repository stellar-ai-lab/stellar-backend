from typing import List

from fastapi import APIRouter, Depends, Request, status

from stellar.account.schemas import (
    CreateUserAccountResponse,
    LoginRequest,
    TestAccountCreation,
    UserAccountCreation,
    UserAccountResponse,
)
from stellar.account.service import AccountService
from stellar.dependencies import (
    AuthDependency,
    get_account_service,
)
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/account", tags=["Account Service Endpoints"])


# FOR LOCAL DEVELOPMENT TESTING ONLY
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def sign_up(
    payload: TestAccountCreation,
    service: AccountService = Depends(get_account_service),
):
    return await service.sign_up(payload)


# FOR LOCAL DEVELOPMENT TESTING ONLY
@router.post("/login")
async def login(
    request: Request,
    payload: LoginRequest,
    auth: AuthDependency,
    service: AccountService = Depends(get_account_service),
):
    """Login user."""
    return await service.login(payload, auth.client)


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
    return await service.create_user_account(payload, auth)
