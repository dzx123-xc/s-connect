from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class PlayerProfileBase(BaseModel):
    sport_id: Optional[int] = None
    position_id: Optional[int] = None
    location_id: Optional[int] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    achievements: Optional[List[Dict[str, Any]]] = None


class PlayerProfileCreate(PlayerProfileBase):
    pass


class PlayerProfileUpdate(PlayerProfileBase):
    pass


class PlayerProfileResponse(PlayerProfileBase):
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CoachProfileBase(BaseModel):
    sport_id: Optional[int] = None
    certifications: Optional[List[Dict[str, Any]]] = None
    experience_years: Optional[int] = None
    clubs_coached: Optional[List[Dict[str, Any]]] = None


class CoachProfileCreate(CoachProfileBase):
    pass


class CoachProfileUpdate(CoachProfileBase):
    pass


class CoachProfileResponse(CoachProfileBase):
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClubProfileBase(BaseModel):
    name: str
    sport_id: Optional[int] = None
    location_id: Optional[int] = None
    description: Optional[str] = None
    founded_year: Optional[int] = None


class ClubProfileCreate(ClubProfileBase):
    pass


class ClubProfileUpdate(ClubProfileBase):
    pass


class ClubProfileResponse(ClubProfileBase):
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrganizerProfileBase(BaseModel):
    organization_name: str
    sports_organized: Optional[List[int]] = None
    license_number: Optional[str] = None


class OrganizerProfileCreate(OrganizerProfileBase):
    pass


class OrganizerProfileUpdate(OrganizerProfileBase):
    pass


class OrganizerProfileResponse(OrganizerProfileBase):
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RefereeProfileBase(BaseModel):
    sport_id: Optional[int] = None
    certification_level: Optional[str] = None


class RefereeProfileCreate(RefereeProfileBase):
    pass


class RefereeProfileUpdate(RefereeProfileBase):
    pass


class RefereeProfileResponse(RefereeProfileBase):
    user_id: int
    matches_officiated: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    phone: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProfileResponse(BaseModel):
    user: UserResponse
    player: Optional[PlayerProfileResponse] = None
    coach: Optional[CoachProfileResponse] = None
    club: Optional[ClubProfileResponse] = None
    organizer: Optional[OrganizerProfileResponse] = None
    referee: Optional[RefereeProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)


__all__ = [
    "UserResponse",
    "ProfileResponse",
    "PlayerProfileBase",
    "PlayerProfileCreate",
    "PlayerProfileUpdate",
    "PlayerProfileResponse",
    "CoachProfileBase",
    "CoachProfileCreate",
    "CoachProfileUpdate",
    "CoachProfileResponse",
    "ClubProfileBase",
    "ClubProfileCreate",
    "ClubProfileUpdate",
    "ClubProfileResponse",
    "OrganizerProfileBase",
    "OrganizerProfileCreate",
    "OrganizerProfileUpdate",
    "OrganizerProfileResponse",
    "RefereeProfileBase",
    "RefereeProfileCreate",
    "RefereeProfileUpdate",
    "RefereeProfileResponse",
]