import logging
from datetime import date, datetime, time, timedelta
from typing import List, Optional
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from postgrest.exceptions import APIError

from stellar.attendance.schemas import (
    AttendanceLogResponse,
    ClockInResponse,
    ClockOutCreation,
    ClockOutResponse,
    TodayStatusResponse,
)
from stellar.auth_context import AuthContext

log = logging.getLogger(__name__)


class AttendanceService:
    """Attendance service."""

    ATTENDANCE_LOGS_TABLE = "attendance_logs"
    TIME_ZONE = ZoneInfo("Asia/Manila")

    async def get_today_status(self, auth: AuthContext) -> TodayStatusResponse:
        """Get the today's status of the user.

        Args:
            auth: Authentication context.

        Returns:
            Today status response.
        """
        current_user_id = auth.current_user_id
        supabase = auth.client
        try:
            now = datetime.now(self.TIME_ZONE)
            today = now.date()

            existing = (
                await supabase.table(self.ATTENDANCE_LOGS_TABLE)
                .select("*")
                .eq("user_id", current_user_id)
                .eq("date", today.isoformat())
                .execute()
            )
            if not existing.data or not existing.data[0]:
                return TodayStatusResponse(can_clock_in=True, can_clock_out=False)

            if not existing.data[0]["time_out"]:
                return TodayStatusResponse(can_clock_in=False, can_clock_out=True)

            return TodayStatusResponse(can_clock_in=False, can_clock_out=False)

        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to get today's status: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get today's status",
            )
        except Exception as e:
            log.exception(f"Failed to get today's status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def get_attendance_history(
        self,
        auth: AuthContext,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[AttendanceLogResponse]:
        """Get the attendance history of the user.

        Args:
            auth: Authentication context.
            start_date: Start date.
            end_date: End date.

        Returns:
            Attendance history response.
        """
        current_user_id = auth.current_user_id
        supabase = auth.client
        try:
            now = datetime.now(self.TIME_ZONE)
            today = now.date()

            if (start_date is None) ^ (end_date is None):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_date and end_date must be provided together",
                )

            if start_date is None and end_date is None:
                # Monday-Sunday
                week_start = today - timedelta(days=today.weekday())
                week_end = week_start + timedelta(days=6)
            else:
                if start_date > end_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="start_date must be <= end_date",
                    )
                week_start = start_date
                week_end = end_date

            response = (
                await supabase.table(self.ATTENDANCE_LOGS_TABLE)
                .select("*")
                .eq("user_id", current_user_id)
                .gte("date", week_start.isoformat())
                .lte("date", week_end.isoformat())
                .execute()
            )

            attendance_logs = []
            for attendance in response.data or []:
                attendance_logs.append(AttendanceLogResponse(**attendance))

            return attendance_logs

        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to get attendance history: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get attendance history",
            )
        except Exception as e:
            log.exception(f"Failed to get attendance history: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def user_clock_in(self, auth: AuthContext) -> ClockInResponse:
        """Clock in a user.

        Args:
            auth: Authentication context.

        Returns:
            Clock in response.
        """
        current_user_id = auth.current_user_id
        supabase = auth.client
        try:
            now = datetime.now(self.TIME_ZONE)
            today = now.date()

            existing = (
                await supabase.table(self.ATTENDANCE_LOGS_TABLE)
                .select("user_id")
                .eq("user_id", current_user_id)
                .eq("date", today.isoformat())
                .execute()
            )
            if existing.data:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User already clocked in today",
                )

            is_late = now.time() > time(9, 0, 0)

            data = {
                "user_id": current_user_id,
                "date": today.isoformat(),
                "time_in": now.isoformat(),
                "is_late": is_late,
            }

            response = (
                await supabase.table(self.ATTENDANCE_LOGS_TABLE).insert(data).execute()
            )
            if not response.data or not response.data[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to clock in user",
                )

            return ClockInResponse(**response.data[0])

        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to clock in user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to clock in user",
            )
        except Exception as e:
            log.exception(f"Failed to clock in user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )

    async def user_clock_out(
        self, auth: AuthContext, payload: ClockOutCreation
    ) -> ClockOutResponse:
        """Clock out a user.

        Args:
            auth: Authentication context.
            payload: Clock out creation payload.

        Returns:
            Clock out response.
        """
        current_user_id = auth.current_user_id
        supabase = auth.client
        try:
            now = datetime.now(self.TIME_ZONE)
            today = now.date()

            existing = (
                await supabase.table(self.ATTENDANCE_LOGS_TABLE)
                .select("*")
                .eq("user_id", current_user_id)
                .eq("date", today.isoformat())
                .execute()
            )
            if not existing.data or not existing.data[0]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User has not clocked in today",
                )
            if existing.data[0]["time_out"]:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User has already clocked out today",
                )

            data = {
                "time_out": now.isoformat(),
                "notes": payload.notes,
            }

            response = (
                await supabase.table(self.ATTENDANCE_LOGS_TABLE)
                .update(data)
                .eq("user_id", current_user_id)
                .eq("date", today.isoformat())
                .execute()
            )
            if not response.data or not response.data[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to clock out user",
                )

            return ClockOutResponse(**response.data[0])

        except HTTPException:
            raise
        except APIError as e:
            log.exception(f"Failed to clock out user: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to clock out user",
            )
        except Exception as e:
            log.exception(f"Failed to clock out user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            )


attendance_service = AttendanceService()
