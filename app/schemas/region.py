from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class RegionBase(BaseModel):
    name: str
    code: str
    is_active: bool = True


class RegionCreate(RegionBase):
    pass


class RegionUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    is_active: Optional[bool] = None


class RegionResponse(RegionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RegionDetailResponse(RegionResponse):
    pricing: List[dict] = []

    class Config:
        from_attributes = True