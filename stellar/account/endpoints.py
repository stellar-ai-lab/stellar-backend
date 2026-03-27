from fastapi import APIRouter, Depends, status
from supabase import AsyncClient

from stellar.account.schemas import CreateUserAccount
from stellar.account.service import AccountService
from stellar.dependencies import (
    get_account_service,
    get_current_user_token,
    get_supabase_client,
)

router = APIRouter(prefix="/account", tags=["Account Service Endpoints"])


# @router.get("/")
# async def get_user_account(
#     user_id: str = Depends(get_current_user),
#     supabase: AsyncClient = Depends(get_supabase_client),
#     service: AccountService = Depends(get_account_service),
# ):
#     """Get the user account."""
#     return await service.get_user_account(user_id, supabase)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user_account(
    payload: CreateUserAccount,
    token: str = Depends(get_current_user_token),
    supabase: AsyncClient = Depends(get_supabase_client),
    service: AccountService = Depends(get_account_service),
):
    """Create new user account."""
    return await service.create_user_account(payload, token, supabase)
