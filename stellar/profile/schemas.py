from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from stellar.enums import AccountStatus, Gender, JobTitle


class ProfileBase(BaseModel):
    first_name: str
    last_name: str
    gender: Gender
    bio: Optional[str] = None
    birth_date: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    job_title: Optional[JobTitle] = JobTitle.CL13
    team_id: Optional[str] = None
    project_id: Optional[str] = None
    account_status: AccountStatus
    onboarded: bool


class CreateProfile(ProfileBase):
    pass


class UpdateProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    birth_date: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    job_title: Optional[JobTitle] = None
    team_id: Optional[str] = None
    project_id: Optional[str] = None
    account_status: Optional[AccountStatus] = None
    onboarded: Optional[bool] = None


class PublicProfile(BaseModel):
    id: str
    user_id: str
    first_name: str
    last_name: str
    gender: Gender
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    job_title: Optional[JobTitle] = None
    team_id: Optional[str] = None
    project_id: Optional[str] = None


class Profile(ProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
