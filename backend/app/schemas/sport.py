from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SportBase(BaseModel):
    name: str
    slug: str
    icon: Optional[str] = None
    is_active: bool = True


class SportCreate(SportBase):
    pass


class SportResponse(SportBase):
    id: int

    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    sport_id: int
    name: str
    abbreviation: Optional[str] = None


class PositionCreate(PositionBase):
    pass


class PositionResponse(PositionBase):
    id: int

    class Config:
        from_attributes = True