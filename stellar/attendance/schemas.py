from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AttendanceBase(BaseModel):
    user_id: UUID
    date: datetime
    time_in: datetime
    time_out: datetime
    is_late: bool


class ClockOut(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None


class ClockInResponse(BaseModel):
    id: UUID
    user_id: UUID
    time_in: datetime
    is_late: bool
    created_at: datetime
    updated_at: datetime


class AttendanceResponse(AttendanceBase):
    id: UUID
    notes: Optional[str] = None
    status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
