from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None


class TeamCreation(TeamBase):
    pass


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class TeamResponse(TeamBase):
    id: UUID
    created_by: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TeamMemberBase(BaseModel):
    user_id: UUID


class TeamMemberCreation(TeamMemberBase):
    pass


class TeamMemberUpdate(BaseModel):
    team_id: Optional[UUID] = None
    user_id: Optional[UUID] = None


class TeamMemberResponse(TeamMemberBase):
    id: UUID
    team_id: UUID
    added_by: UUID
    created_at: datetime
    updated_at: datetime
