from fastapi import APIRouter, Depends, Request, status

from stellar.account.schemas import CreateUserAccount
from stellar.account.service import AccountService
from stellar.dependencies import (
    AuthDependency,
    get_account_service,
)
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/account", tags=["Account Service Endpoints"])


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_user_account(
    request: Request,
    payload: CreateUserAccount,
    auth: AuthDependency,
    service: AccountService = Depends(get_account_service),
):
    """Create new user account."""
    return await service.create_user_account(payload, auth.token, auth.client)
