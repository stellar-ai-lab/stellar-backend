from fastapi import APIRouter, Depends, status

from stellar.dependencies import get_dev_service
from stellar.dev.schemas import (
    LoginRequest,
    LoginResponse,
    TestAccountCreation,
    TestAccountResponse,
)
from stellar.dev.service import DevService

router = APIRouter(prefix="/dev", tags=["Dev Endpoints"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_test_account(
    payload: TestAccountCreation,
    service: DevService = Depends(get_dev_service),
) -> TestAccountResponse:
    """Create a new test account."""
    return await service.create_test_account(payload)


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_test_account(
    payload: LoginRequest,
    service: DevService = Depends(get_dev_service),
) -> LoginResponse:
    """Login test account."""
    return await service.login_test_account(payload)
