import logging
from datetime import datetime, time
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from postgrest.exceptions import APIError

from stellar.attendance.schemas import ClockInResponse
from stellar.auth_context import AuthContext

log = logging.getLogger(__name__)


class AttendanceService:
    """Attendance service."""

    ATTENDANCE_LOGS_TABLE = "attendance_logs"
    TIME_ZONE = ZoneInfo("Asia/Manila")

    async def user_clock_in(self, auth: AuthContext) -> ClockInResponse:
        """Clock in a user."""
        current_user_id = auth.current_user_id
        supabase = auth.client
        try:
            now = datetime.now(self.TIME_ZONE)
            today = now.date()

            existing = (
                await supabase.table(self.ATTENDANCE_LOGS_TABLE)
                .select("user_id")
                .eq("user_id", current_user_id)
                .eq("date", today)
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
                "date": today,
                "time_in": now,
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


attendance_service = AttendanceService()
