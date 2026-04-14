from fastapi import APIRouter, Depends, Request, status

from stellar.attendance.schemas import ClockInResponse
from stellar.attendance.service import AttendanceService
from stellar.dependencies import AuthDependency, get_attendance_service
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/attendance", tags=["Attendance Endpoints"])


@router.post("/clock-in", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def user_clock_in(
    request: Request,
    auth: AuthDependency,
    service: AttendanceService = Depends(get_attendance_service),
) -> ClockInResponse:
    """Clock in a user."""
    return await service.user_clock_in(auth)
