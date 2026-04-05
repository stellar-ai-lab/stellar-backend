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
