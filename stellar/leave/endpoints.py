from typing import List

from fastapi import APIRouter, Depends, Request, status

from stellar.dependencies import AuthDependency, get_leave_service
from stellar.leave.schemas import (
    ApproverResponse,
    LeaveRequestCreation,
    LeaveResponse,
)
from stellar.leave.service import LeaveService
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/leave", tags=["Leave Endpoints"])


@router.get("/", status_code=status.HTTP_200_OK)
@limiter.limit("15/minute")
async def get_list_of_leave_requests(
    request: Request,
    auth: AuthDependency,
    service: LeaveService = Depends(get_leave_service),
) -> List[LeaveResponse]:
    """Get the list of leaves."""
    return await service.get_list_of_leaves(auth)


@router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("15/minute")
async def create_leave_request(
    request: Request,
    payload: LeaveRequestCreation,
    auth: AuthDependency,
    service: LeaveService = Depends(get_leave_service),
) -> LeaveResponse:
    """Create a new leave request."""
    return await service.create_leave_request(auth, payload)


@router.get("/approver", status_code=status.HTTP_200_OK)
@limiter.limit("15/minute")
async def get_list_of_approvers(
    request: Request,
    auth: AuthDependency,
    service: LeaveService = Depends(get_leave_service),
) -> List[ApproverResponse]:
    """Get the list of approvers."""
    return await service.get_list_of_approvers(auth)
