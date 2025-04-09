from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.database import Base


class ProductAttributeValue(Base):
    __tablename__ = "product_attribute_values"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    attribute_value_id = Column(Integer, ForeignKey("attribute_values.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="attribute_values")
    attribute_value = relationship("AttributeValue", back_populates="products")

    # Ensure a product doesn't have the same attribute value multiple times
    __table_args__ = (
        UniqueConstraint('product_id', 'attribute_value_id', name='uix_product_attribute_value'),
    )