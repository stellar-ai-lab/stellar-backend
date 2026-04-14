import logging
from datetime import datetime, time
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from postgrest.exceptions import APIError

from stellar.attendance.schemas import (
    ClockInResponse,
    ClockOutCreation,
    ClockOutResponse,
)
from stellar.auth_context import AuthContext

log = logging.getLogger(__name__)


class AttendanceService:
    """Attendance service."""

    ATTENDANCE_LOGS_TABLE = "attendance_logs"
    TIME_ZONE = ZoneInfo("Asia/Manila")

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
