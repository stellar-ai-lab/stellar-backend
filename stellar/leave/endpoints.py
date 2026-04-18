from fastapi import APIRouter, Depends, Request, status

from stellar.dependencies import AuthDependency, get_leave_service
from stellar.leave.schemas import LeaveRequestCreation, LeaveRequestResponse
from stellar.leave.service import LeaveService
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/leave", tags=["Leave Endpoints"])


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("15/minute")
async def create_leave_request(
    request: Request,
    payload: LeaveRequestCreation,
    auth: AuthDependency,
    service: LeaveService = Depends(get_leave_service),
) -> LeaveRequestResponse:
    """Create a new leave request."""
    return await service.create_leave_request(auth, payload)
