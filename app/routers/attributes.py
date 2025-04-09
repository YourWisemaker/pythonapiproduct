from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.attribute import Attribute
from app.schemas.attribute import AttributeCreate, AttributeUpdate, AttributeResponse, AttributeDetailResponse

router = APIRouter()


# Attribute endpoints
@router.post("/attributes", response_model=AttributeResponse, status_code=status.HTTP_201_CREATED)
def create_attribute(attribute: AttributeCreate, db: Session = Depends(get_db)):
    # Check for duplicate attribute
    existing_attribute = db.query(Attribute).filter(Attribute.name == attribute.name).first()
    if existing_attribute:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attribute with this name already exists.")
    
    db_attribute = Attribute(**attribute.dict())
    db.add(db_attribute)
    db.commit()
    db.refresh(db_attribute)
    return db_attribute


@router.get("/attributes", response_model=List[AttributeResponse])
def read_attributes(
    skip: int = 0, 
    limit: int = 100, 
    name: Optional[str] = None,
    type: Optional[str] = None,
    is_filterable: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Attribute)
    
    if name:
        query = query.filter(Attribute.name.ilike(f"%{name}%"))
    
    if type:
        query = query.filter(Attribute.type == type)
    
    if is_filterable is not None:
        query = query.filter(Attribute.is_filterable == is_filterable)
    
    return query.offset(skip).limit(limit).all()


@router.get("/attributes/{attribute_id}", response_model=AttributeDetailResponse)
def read_attribute(attribute_id: int, db: Session = Depends(get_db)):
    db_attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if db_attribute is None:
        raise HTTPException(status_code=404, detail="Attribute not found")
    return db_attribute


@router.put("/attributes/{attribute_id}", response_model=AttributeResponse)
def update_attribute(attribute_id: int, attribute: AttributeUpdate, db: Session = Depends(get_db)):
    db_attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if db_attribute is None:
        raise HTTPException(status_code=404, detail="Attribute not found")
    
    # Check for duplicate attribute
    duplicate_attribute = db.query(Attribute).filter(Attribute.name == attribute.name, Attribute.id != attribute_id).first()
    if duplicate_attribute:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Attribute with this name already exists.")

    for key, value in attribute.dict(exclude_unset=True).items():
        setattr(db_attribute, key, value)
    
    db.commit()
    db.refresh(db_attribute)
    return db_attribute


@router.delete("/attributes/{attribute_id}", status_code=status.HTTP_200_OK)
def delete_attribute(attribute_id: int, db: Session = Depends(get_db)):
    db_attribute = db.query(Attribute).filter(Attribute.id == attribute_id).first()
    if db_attribute is None:
        raise HTTPException(status_code=404, detail="Attribute not found")
    
    db.delete(db_attribute)
    db.commit()
    return {"detail": "Attribute has been deleted"}