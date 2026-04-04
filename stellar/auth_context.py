from dataclasses import dataclass

from supabase import AsyncClient


@dataclass
class AuthContext:
    """Authentication context."""

    client: AsyncClient
    current_user_id: str
    current_user_name: str
    token: str
    role: str
