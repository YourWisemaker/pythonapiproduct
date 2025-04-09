from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.region import Region
from app.schemas.region import RegionCreate, RegionUpdate, RegionResponse, RegionDetailResponse

router = APIRouter()


@router.post("/regions", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
def create_region(region: RegionCreate, db: Session = Depends(get_db)):
    # Check for duplicate region
    existing_region = db.query(Region).filter(Region.name == region.name).first()
    if existing_region:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Region with this name already exists.")
    
    db_region = Region(**region.dict())
    db.add(db_region)
    db.commit()
    db.refresh(db_region)
    return db_region


@router.get("/regions", response_model=List[RegionResponse])
def read_regions(
    skip: int = 0, 
    limit: int = 100, 
    name: Optional[str] = None,
    code: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Region)
    
    if name:
        query = query.filter(Region.name.ilike(f"%{name}%"))
    
    if code:
        query = query.filter(Region.code == code)
    
    if is_active is not None:
        query = query.filter(Region.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/regions/{region_id}", response_model=RegionDetailResponse)
def read_region(region_id: int, db: Session = Depends(get_db)):
    db_region = db.query(Region).filter(Region.id == region_id).first()
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Get pricing information
    pricing = []
    for price in db_region.pricing:
        pricing.append({
            "id": price.id,
            "product": {
                "id": price.product.id,
                "name": price.product.name,
                "sku": price.product.sku
            },
            "rental_period": {
                "id": price.rental_period.id,
                "name": price.rental_period.name,
                "days": price.rental_period.days
            },
            "price": float(price.price),
            "is_active": price.is_active
        })
    
    # Create response with nested data
    response = RegionDetailResponse(
        id=db_region.id,
        name=db_region.name,
        code=db_region.code,
        is_active=db_region.is_active,
        created_at=db_region.created_at,
        updated_at=db_region.updated_at,
        pricing=pricing
    )
    
    return response


@router.put("/regions/{region_id}", response_model=RegionResponse)
def update_region(region_id: int, region: RegionUpdate, db: Session = Depends(get_db)):
    db_region = db.query(Region).filter(Region.id == region_id).first()
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    
    # Check for duplicate region
    duplicate_region = db.query(Region).filter(Region.name == region.name, Region.id != region_id).first()
    if duplicate_region:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Region with this name already exists.")

    for key, value in region.dict(exclude_unset=True).items():
        setattr(db_region, key, value)
    
    db.commit()
    db.refresh(db_region)
    return db_region


@router.delete("/regions/{region_id}", status_code=status.HTTP_200_OK)
def delete_region(region_id: int, db: Session = Depends(get_db)):
    db_region = db.query(Region).filter(Region.id == region_id).first()
    if db_region is None:
        raise HTTPException(status_code=404, detail="Region not found")
    
    db.delete(db_region)
    db.commit()
    return {"detail": "Region has been deleted"}