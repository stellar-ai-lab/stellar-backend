from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TeamCreation(BaseModel):
    name: str
    description: Optional[str] = None


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TeamResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_by: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TeamMemberCreation(BaseModel):
    user_id: UUID


class TeamMemberResponse(BaseModel):
    id: UUID
    team_id: UUID
    user_id: UUID
    added_by: str
    created_at: datetime
    updated_at: datetime
