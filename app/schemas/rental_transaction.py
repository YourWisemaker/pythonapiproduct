from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
import enum


class TransactionStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class RentalTransactionBase(BaseModel):
    product_id: int
    region_id: int
    rental_period_id: int
    customer_name: str
    customer_email: str
    customer_address: str
    start_date: datetime
    end_date: datetime
    price: Decimal
    status: TransactionStatus = TransactionStatus.CONFIRMED
    notes: Optional[str] = None


class RentalTransactionCreate(RentalTransactionBase):
    pass


class RentalTransactionUpdate(BaseModel):
    product_id: Optional[int] = None
    region_id: Optional[int] = None
    rental_period_id: Optional[int] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_address: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    price: Optional[Decimal] = None
    status: Optional[TransactionStatus] = None
    notes: Optional[str] = None


class RentalTransactionResponse(RentalTransactionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class RentalTransactionDetailResponse(RentalTransactionResponse):
    product: Dict[str, Any] = {}
    region: Dict[str, Any] = {}
    rental_period: Dict[str, Any] = {}

    class Config:
        orm_mode = True