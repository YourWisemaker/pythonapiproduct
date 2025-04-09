from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from app.database import Base


class RentalPeriod(Base):
    __tablename__ = "rental_periods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., Daily, Weekly, Monthly
    days = Column(Integer, nullable=False)  # Number of days in this period
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    pricing = relationship("ProductPricing", back_populates="rental_period")
    rental_transactions = relationship("RentalTransaction", back_populates="rental_period")