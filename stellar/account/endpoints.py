from fastapi import APIRouter, Depends, Request, status

from stellar.account.schemas import AccountCreation, AccountResponse
from stellar.account.service import AccountService
from stellar.dependencies import AuthDependency, get_account_service
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/account", tags=["Account Endpoints"])


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_user_account(
    request: Request,
    payload: AccountCreation,
    auth: AuthDependency,
    service: AccountService = Depends(get_account_service),
) -> AccountResponse:
    """Create a new user account."""
    return await service.create_user_account(payload, auth)
