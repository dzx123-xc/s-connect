from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = Field(pattern="^(player|coach|club|organizer|referee)$")

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
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        allowed = {"player", "coach", "club", "organizer", "referee"}
        if v not in allowed:
            raise ValueError(f"Role must be one of: {allowed}")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse
    redirect_url: str