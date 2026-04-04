from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from stellar.enums import AccountStatus, JobTitle, UserRole


class UserAccountBase(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str
    last_name: str
    job_title: JobTitle
    role: UserRole
    team: str
    created_by: str
    status: AccountStatus


class UserAccountCreation(UserAccountBase):
    pass


class UserAccountResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    job_title: JobTitle
    team: str
    role: UserRole
    status: AccountStatus
    created_by: str
    created_at: datetime
    updated_at: datetime


class CreateUserAccountResponse(BaseModel):
    id: UUID
    email: str
    role: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
