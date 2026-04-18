from enum import StrEnum


class UserRole(StrEnum):
    DEVELOPER = "developer"
    LEADERSHIP = "leadership"
    MANAGER = "manager"
    LEAD = "lead"
    SUPPORT = "support"
    IC = "ic"


class AdminRole(StrEnum):
    DEVELOPER = "developer"
    LEADERSHIP = "leadership"
    MANAGER = "manager"


class AccountStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class JobTitle(StrEnum):
    CL13 = "CL13"
    CL12 = "CL12"
    CL11 = "CL11"
    CL10 = "CL10"
    CL9 = "CL9"
    CL8 = "CL8"
    CL7 = "CL7"
    CL6 = "CL6"
    CL5 = "CL5"


class LeaveType(StrEnum):
    VL = "VL"
    SL = "SL"
    ML = "ML"
    PL = "PL"
    EL = "EL"
