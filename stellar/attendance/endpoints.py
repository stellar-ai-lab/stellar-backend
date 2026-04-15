from typing import List

from fastapi import APIRouter, Depends, Request, status

from stellar.attendance.schemas import (
    AttendanceLogResponse,
    ClockInResponse,
    ClockOutCreation,
    ClockOutResponse,
    TodayStatusResponse,
)
from stellar.attendance.service import AttendanceService
from stellar.dependencies import AuthDependency, get_attendance_service
from stellar.rate_limiter import limiter

router = APIRouter(prefix="/attendance", tags=["Attendance Endpoints"])


@router.get("/today-status", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def get_today_status(
    request: Request,
    auth: AuthDependency,
    service: AttendanceService = Depends(get_attendance_service),
) -> TodayStatusResponse:
    """Get the today's status of the user."""
    return await service.get_today_status(auth)


@router.get("/history", status_code=status.HTTP_200_OK)
@limiter.limit("20/minute")
async def get_attendance_history(
    request: Request,
    auth: AuthDependency,
    service: AttendanceService = Depends(get_attendance_service),
) -> List[AttendanceLogResponse]:
    """Get the attendance history of the user."""
    return await service.get_attendance_history(auth)


@router.post("/clock-in", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def user_clock_in(
    request: Request,
    auth: AuthDependency,
    service: AttendanceService = Depends(get_attendance_service),
) -> ClockInResponse:
    """Clock in a user."""
    return await service.user_clock_in(auth)


@router.patch("/clock-out", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def user_clock_out(
    request: Request,
    payload: ClockOutCreation,
    auth: AuthDependency,
    service: AttendanceService = Depends(get_attendance_service),
) -> ClockOutResponse:
    """Clock out a user."""
    return await service.user_clock_out(auth, payload)
