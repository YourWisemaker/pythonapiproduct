from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductPricingBase(BaseModel):
    product_id: int
    region_id: int
    rental_period_id: int
    price: Decimal
    is_active: bool = True


class ProductPricingCreate(ProductPricingBase):
    pass


class ProductPricingUpdate(BaseModel):
    product_id: Optional[int] = None
    region_id: Optional[int] = None
    rental_period_id: Optional[int] = None
    price: Optional[Decimal] = None
    is_active: Optional[bool] = None


class ProductPricingResponse(ProductPricingBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductPricingDetailResponse(ProductPricingResponse):
    product: dict = {}
    region: dict = {}
    rental_period: dict = {}

    class Config:
        from_attributes = True