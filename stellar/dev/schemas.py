from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from stellar.enums import UserRole


class TestAccountBase(BaseModel):
    email: EmailStr
    password: str


class TestAccountCreation(TestAccountBase):
    created_by: str
    role: UserRole


class TestAccountResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    created_at: datetime
    updated_at: datetime


class LoginRequest(TestAccountBase):
    pass


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
