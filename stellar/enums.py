from enum import StrEnum


class UserRole(StrEnum):
    DEVELOPER = "developer"
    LEADERSHIP = "leadership"
    MANAGER = "manager"
    LEAD = "lead"
    SUPPORT = "support"
    IC = "ic"


class AllowedCreationRoles(StrEnum):
    DEVELOPER = "developer"
    LEADERSHIP = "leadership"
    MANAGER = "manager"
