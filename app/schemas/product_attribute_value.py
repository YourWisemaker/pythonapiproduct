from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ProductAttributeValueBase(BaseModel):
    product_id: int
    attribute_value_id: int


class ProductAttributeValueCreate(ProductAttributeValueBase):
    pass


class ProductAttributeValueUpdate(BaseModel):
    product_id: Optional[int] = None
    attribute_value_id: Optional[int] = None


class ProductAttributeValueResponse(ProductAttributeValueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductAttributeValueDetailResponse(ProductAttributeValueResponse):
    product: Dict[str, Any] = {}
    attribute_value: Dict[str, Any] = {}

    class Config:
        from_attributes = True