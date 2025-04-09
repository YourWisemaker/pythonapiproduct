from sqlalchemy import Column, Integer, String, Text, Numeric, Enum, ForeignKey, DateTime, Index, func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class TransactionStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class RentalTransaction(Base):
    __tablename__ = "rental_transactions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="RESTRICT"), nullable=False)
    rental_period_id = Column(Integer, ForeignKey("rental_periods.id", ondelete="RESTRICT"), nullable=False)
    customer_name = Column(String, nullable=False)
    customer_email = Column(String, nullable=False)
    customer_address = Column(Text, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.CONFIRMED, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="rental_transactions")
    region = relationship("Region", back_populates="rental_transactions")
    rental_period = relationship("RentalPeriod", back_populates="rental_transactions")

    # Indexes for common query patterns
    __table_args__ = (
        Index('ix_rental_transactions_product_status', 'product_id', 'status'),
        Index('ix_rental_transactions_region_status', 'region_id', 'status'),
        Index('ix_rental_transactions_date_range', 'start_date', 'end_date'),
    )