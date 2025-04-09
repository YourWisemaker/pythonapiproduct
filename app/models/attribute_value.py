from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class AttributeValue(Base):
    __tablename__ = 'attribute_values'

    id = Column(Integer, primary_key=True, index=True)
    attribute_id = Column(Integer, ForeignKey('attributes.id'))
    value = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    attribute = relationship('Attribute', back_populates='values')