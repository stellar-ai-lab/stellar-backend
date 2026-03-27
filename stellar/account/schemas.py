from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from stellar.enums import AccountStatus, UserRole


class CreateUserAccount(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    role: UserRole
    status: AccountStatus


class CreateUserAccountResponse(BaseModel):
    id: UUID
    email: str
    role: str
