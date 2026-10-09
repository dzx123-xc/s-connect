from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class StateBase(BaseModel):
    code: str
    name: str


class StateResponse(StateBase):
    id: int

    class Config:
        from_attributes = True


class DistrictBase(BaseModel):
    state_id: int
    name: str


class DistrictResponse(DistrictBase):
    id: int

    class Config:
        from_attributes = True


class CityBase(BaseModel):
    district_id: int
    name: str
    type: str


class CityResponse(CityBase):
    id: int

    class Config:
        from_attributes = True


class VillageBase(BaseModel):
    city_id: int
    name: str


class VillageResponse(VillageBase):
    id: int

    class Config:
        from_attributes = True