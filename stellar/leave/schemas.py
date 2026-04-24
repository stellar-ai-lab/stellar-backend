from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from stellar.enums import JobTitle, LeaveRequestStatus, LeaveType


class LeaveRequestCreation(BaseModel):
    leave_type: LeaveType
    start_date: date
    end_date: date
    approver: List[UUID]
    reason: Optional[str] = None


class LeaveResponse(BaseModel):
    id: UUID
    user_id: UUID
    leave_type: LeaveType
    start_date: date
    end_date: date
    total_days: int
    reason: Optional[str] = None
    status: LeaveRequestStatus
    approver: List[UUID]
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ApproverResponse(BaseModel):
    id: UUID
    user_id: UUID
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    job_title: JobTitle
