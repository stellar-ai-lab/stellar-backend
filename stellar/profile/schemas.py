from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from stellar.enums import AccountStatus, Gender, JobTitle


class ProfileBase(BaseModel):
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    gender: Gender
    bio: Optional[str] = None
    birth_date: Optional[datetime] = None
    phone_number: Optional[str] = None
    job_title: JobTitle
    reports_to: str
    account_status: AccountStatus
    onboarded: bool


class ProfileCreation(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    birth_date: Optional[datetime] = None
    phone_number: Optional[str] = None
    job_title: Optional[JobTitle] = None
    reports_to: Optional[str] = None
    account_status: Optional[AccountStatus] = None
    onboarded: Optional[bool] = None


class ProfileResponse(ProfileBase):
    id: str
    user_id: UUID
    created_at: datetime
    updated_at: datetime
