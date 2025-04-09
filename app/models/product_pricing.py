from sqlalchemy import Column, Integer, Numeric, Boolean, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base


class ProductPricing(Base):
    __tablename__ = "product_pricing"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id", ondelete="CASCADE"), nullable=False)
    rental_period_id = Column(Integer, ForeignKey("rental_periods.id", ondelete="CASCADE"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="pricing")
    region = relationship("Region", back_populates="pricing")
    rental_period = relationship("RentalPeriod", back_populates="pricing")

    # Ensure unique pricing for product-region-period combination
    __table_args__ = (
        UniqueConstraint('product_id', 'region_id', 'rental_period_id', name='uix_product_region_period'),
    )