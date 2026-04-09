from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr

from stellar.enums import UserRole


class AccountBase(BaseModel):
    email: EmailStr
    password: str
    role: UserRole


class AccountCreation(AccountBase):
    pass


class AccountResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: UserRole
    created_by: UUID
    created_at: datetime
    updated_at: datetime
