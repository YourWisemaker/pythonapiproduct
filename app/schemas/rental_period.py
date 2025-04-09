from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RentalPeriodBase(BaseModel):
    name: str
    days: int
    is_active: bool = True


class RentalPeriodCreate(RentalPeriodBase):
    pass


class RentalPeriodUpdate(BaseModel):
    name: Optional[str] = None
    days: Optional[int] = None
    is_active: Optional[bool] = None


class RentalPeriodResponse(RentalPeriodBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RentalPeriodDetailResponse(RentalPeriodResponse):
    pricing: List[dict] = []

    class Config:
        orm_mode = True