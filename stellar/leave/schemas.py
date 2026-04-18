from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from stellar.enums import LeaveRequestStatus, LeaveType


class LeaveRequestCreation(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    approver: UUID
    reason: Optional[str] = None


class LeaveRequestResponse(BaseModel):
    id: UUID
    user_id: UUID
    leave_type: LeaveType
    start_date: date
    end_date: date
    total_days: int
    reason: Optional[str] = None
    status: LeaveRequestStatus
    approver: UUID
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
