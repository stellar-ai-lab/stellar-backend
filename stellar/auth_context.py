from dataclasses import dataclass

from supabase import AsyncClient


@dataclass
class AuthContext:
    """Authentication context."""

    client: AsyncClient
    current_user_id: str
    token: str
    role: str
