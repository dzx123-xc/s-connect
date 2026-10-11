from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.schemas.user import (
    UserResponse,
    PlayerProfileResponse,
    CoachProfileResponse,
    ClubProfileResponse,
    OrganizerProfileResponse,
    RefereeProfileResponse,
)

PUBLIC_ROLES = {"player", "coach", "club", "organizer", "referee"}
ALL_ROLES = PUBLIC_ROLES | {"admin"}


def _password_requirements(password: str) -> List[str]:
    """Return a list of unmet password requirements."""
    issues: List[str] = []
    if len(password) < 8:
        issues.append("Password must be at least 8 characters")
    if not any(c.isupper() for c in password):
        issues.append("Password must contain an uppercase letter")
    if not any(c.islower() for c in password):
        issues.append("Password must contain a lowercase letter")
    if not any(c.isdigit() for c in password):
        issues.append("Password must contain a number")
    if not any(not c.isalnum() for c in password):
        issues.append("Password must contain a special character")
    return issues


def validate_password_strong(password: str) -> str:
    issues = _password_requirements(password)
    if issues:
        raise ValueError("; ".join(issues))
    return password


def validate_public_role(role: str) -> str:
    if role not in PUBLIC_ROLES:
        raise ValueError(
            f"Role must be one of: {sorted(PUBLIC_ROLES)}. Admin registration is not allowed."
        )
    return role


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    username: str = Field(min_length=3, max_length=50)
    phone: str = Field(min_length=5, max_length=20)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str
    availability: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    village: Optional[str] = None

    sport_id: Optional[int] = None
    position_id: Optional[int] = None
    location_id: Optional[int] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    achievements: Optional[List[Dict[str, Any]]] = None

    certifications: Optional[List[Dict[str, Any]]] = None
    experience_years: Optional[int] = None
    clubs_coached: Optional[List[Dict[str, Any]]] = None

    name: Optional[str] = None
    sport_id_club: Optional[int] = None
    description: Optional[str] = None
    founded_year: Optional[int] = None

    organization_name: Optional[str] = None
    sports_organized: Optional[List[int]] = None
    license_number: Optional[str] = None

    sport_id_referee: Optional[int] = None
    certification_level: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strong(v)

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ALL_ROLES:
            raise ValueError(f"Role must be one of: {sorted(ALL_ROLES)}")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("Username is required")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores and hyphens allowed)")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Phone number is required")
        digits = v.lstrip("+")
        if not digits.isdigit():
            raise ValueError("Phone number must contain only digits (optional leading +)")
        if len(digits) < 5 or len(digits) > 15:
            raise ValueError("Phone number must be between 5 and 15 digits")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = " ".join(v.split())
        if not v:
            raise ValueError("Full name is required")
        return v


class LoginRequest(BaseModel):
    identifier: Optional[str] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    password: str

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v or None


class ProfileResponse(BaseModel):
    user: UserResponse
    player: Optional[PlayerProfileResponse] = None
    coach: Optional[CoachProfileResponse] = None
    club: Optional[ClubProfileResponse] = None
    organizer: Optional[OrganizerProfileResponse] = None
    referee: Optional[RefereeProfileResponse] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse
    profile: Optional[ProfileResponse] = None
    role: str
    redirect_url: str


class MeResponse(BaseModel):
    user: UserResponse
    profile: Optional[ProfileResponse] = None
    role: str
    redirect_url: str


__all__ = [
    "RegisterRequest",
    "LoginRequest",
    "UserResponse",
    "ProfileResponse",
    "AuthResponse",
    "MeResponse",
    "PUBLIC_ROLES",
    "ALL_ROLES",
    "validate_password_strong",
    "validate_public_role",
]