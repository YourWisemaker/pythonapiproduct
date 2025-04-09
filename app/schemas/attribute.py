from pydantic import BaseModel
from typing import Optional, List, ForwardRef
from datetime import datetime

# Import after defining AttributeValueResponse to avoid circular imports
from app.schemas.attribute_value import AttributeValueResponse


class AttributeBase(BaseModel):
    name: str
    type: str  # text, number, boolean, etc.
    is_filterable: bool = False
    is_required: bool = False


class AttributeCreate(AttributeBase):
    pass


class AttributeUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    is_filterable: Optional[bool] = None
    is_required: Optional[bool] = None


class AttributeResponse(AttributeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AttributeDetailResponse(AttributeResponse):
    values: List["AttributeValueResponse"] = []

    class Config:
        from_attributes = True