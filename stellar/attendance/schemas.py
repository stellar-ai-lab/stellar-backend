from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TodayStatusResponse(BaseModel):
    can_clock_in: bool
    can_clock_out: bool


class ClockInResponse(BaseModel):
    id: UUID
    user_id: UUID
    time_in: datetime
    is_late: bool
    created_at: datetime
    updated_at: datetime


class ClockOutCreation(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None


class ClockOutResponse(ClockInResponse):
    time_out: datetime
    notes: Optional[str] = None
