from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.attribute import AttributeValue
from app.models.product_attribute_value import ProductAttributeValue
from app.schemas.attribute_value import AttributeValueCreate, AttributeValueUpdate, AttributeValueResponse, AttributeValueDetailResponse

router = APIRouter()

@router.post("/attribute-values", response_model=AttributeValueResponse, status_code=status.HTTP_201_CREATED)
def create_attribute_value(attribute_value: AttributeValueCreate, db: Session = Depends(get_db)):
    # Check for duplicate attribute value
    existing_attribute_value = db.query(AttributeValue).filter(
        AttributeValue.value == attribute_value.value, 
        AttributeValue.attribute_id == attribute_value.attribute_id
    ).first()
    
    if existing_attribute_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="The value already exists for this attribute."
        )
    
    db_attribute_value = AttributeValue(**attribute_value.dict())
    db.add(db_attribute_value)
    db.commit()
    db.refresh(db_attribute_value)
    
    return db_attribute_value

@router.get("/attribute-values", response_model=List[AttributeValueResponse])
def read_attribute_values(
    skip: int = 0, 
    limit: int = 100, 
    attribute_id: Optional[int] = None,
    value: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(AttributeValue)
    
    if attribute_id:
        query = query.filter(AttributeValue.attribute_id == attribute_id)
    
    if value:
        query = query.filter(AttributeValue.value.ilike(f"%{value}%"))
    
    return query.offset(skip).limit(limit).all()

@router.get("/attribute-values/{attribute_value_id}", response_model=AttributeValueDetailResponse)
def read_attribute_value(attribute_value_id: int, db: Session = Depends(get_db)):
    db_attribute_value = db.query(AttributeValue).filter(AttributeValue.id == attribute_value_id).first()
    if not db_attribute_value:
        raise HTTPException(status_code=404, detail="Attribute value not found")
    
    return db_attribute_value

@router.put("/attribute-values/{attribute_value_id}", response_model=AttributeValueResponse)
def update_attribute_value(attribute_value_id: int, attribute_value: AttributeValueUpdate, db: Session = Depends(get_db)):
    db_attribute_value = db.query(AttributeValue).filter(AttributeValue.id == attribute_value_id).first()
    if not db_attribute_value:
        raise HTTPException(status_code=404, detail="Attribute value not found")
    
    # Check for duplicate attribute value
    duplicate_attribute_value = db.query(AttributeValue).filter(
        AttributeValue.value == attribute_value.value,
        AttributeValue.attribute_id == attribute_value.attribute_id,
        AttributeValue.id != attribute_value_id
    ).first()
    
    if duplicate_attribute_value:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="The value already exists for this attribute."
        )

    for key, value in attribute_value.dict(exclude_unset=True).items():
        setattr(db_attribute_value, key, value)
    
    db.commit()
    db.refresh(db_attribute_value)
    return db_attribute_value

@router.delete("/attribute-values/{attribute_value_id}", status_code=status.HTTP_200_OK)
def delete_attribute_value(attribute_value_id: int, db: Session = Depends(get_db)):
    db_attribute_value = db.query(AttributeValue).filter(AttributeValue.id == attribute_value_id).first()
    if db_attribute_value is None:
        raise HTTPException(status_code=404, detail="Attribute value not found")
    
    # Check if attribute value is used in products
    in_use = db.query(ProductAttributeValue).filter(
        ProductAttributeValue.attribute_value_id == attribute_value_id
    ).first()
    
    if in_use:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot delete attribute value that is in use by products."
        )
    
    db.delete(db_attribute_value)
    db.commit()
    return {"detail": "Attribute value deleted successfully"}