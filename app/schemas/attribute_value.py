from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AttributeBase(BaseModel):
    name: str
    type: str


class AttributeValueBase(BaseModel):
    attribute_id: int
    value: str


class AttributeValueCreate(AttributeValueBase):
    pass


class AttributeValueUpdate(BaseModel):
    attribute_id: Optional[int] = None
    value: Optional[str] = None


class AttributeInValueResponse(AttributeBase):
    id: int

    class Config:
        orm_mode = True
        from_attributes = True


class AttributeValueResponse(BaseModel):
    id: int
    attribute_id: int
    value: str
    attribute: Optional[AttributeInValueResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class AttributeValueDetailResponse(AttributeValueResponse):
    pass