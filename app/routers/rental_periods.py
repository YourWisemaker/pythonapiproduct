from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.rental_period import RentalPeriod
from app.schemas.rental_period import RentalPeriodCreate, RentalPeriodUpdate, RentalPeriodResponse, RentalPeriodDetailResponse

router = APIRouter()


@router.post("/rental-periods", response_model=RentalPeriodResponse, status_code=status.HTTP_201_CREATED)
def create_rental_period(rental_period: RentalPeriodCreate, db: Session = Depends(get_db)):
    # Check for duplicate rental period
    existing_rental_period = db.query(RentalPeriod).filter(RentalPeriod.name == rental_period.name).first()
    if existing_rental_period:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rental period with this name already exists.")
    
    db_rental_period = RentalPeriod(**rental_period.dict())
    db.add(db_rental_period)
    db.commit()
    db.refresh(db_rental_period)
    return db_rental_period


@router.get("/rental-periods", response_model=List[RentalPeriodResponse])
def read_rental_periods(
    skip: int = 0, 
    limit: int = 100, 
    name: Optional[str] = None,
    days: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(RentalPeriod)
    
    if name:
        query = query.filter(RentalPeriod.name.ilike(f"%{name}%"))
    
    if days is not None:
        query = query.filter(RentalPeriod.days == days)
    
    if is_active is not None:
        query = query.filter(RentalPeriod.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/rental-periods/{rental_period_id}", response_model=RentalPeriodDetailResponse)
def read_rental_period(rental_period_id: int, db: Session = Depends(get_db)):
    db_rental_period = db.query(RentalPeriod).filter(RentalPeriod.id == rental_period_id).first()
    if db_rental_period is None:
        raise HTTPException(status_code=404, detail="Rental period not found")
    
    # Get pricing information
    pricing = []
    for price in db_rental_period.pricing:
        pricing.append({
            "id": price.id,
            "product": {
                "id": price.product.id,
                "name": price.product.name,
                "sku": price.product.sku
            },
            "region": {
                "id": price.region.id,
                "name": price.region.name,
                "code": price.region.code
            },
            "price": float(price.price),
            "is_active": price.is_active
        })
    
    # Create response with nested data
    response = RentalPeriodDetailResponse(
        id=db_rental_period.id,
        name=db_rental_period.name,
        days=db_rental_period.days,
        is_active=db_rental_period.is_active,
        created_at=db_rental_period.created_at,
        updated_at=db_rental_period.updated_at,
        pricing=pricing
    )
    
    return response


@router.put("/rental-periods/{rental_period_id}", response_model=RentalPeriodResponse)
def update_rental_period(rental_period_id: int, rental_period: RentalPeriodUpdate, db: Session = Depends(get_db)):
    db_rental_period = db.query(RentalPeriod).filter(RentalPeriod.id == rental_period_id).first()
    if db_rental_period is None:
        raise HTTPException(status_code=404, detail="Rental period not found")
    
    # Check for duplicate rental period
    duplicate_rental_period = db.query(RentalPeriod).filter(RentalPeriod.name == rental_period.name, RentalPeriod.id != rental_period_id).first()
    if duplicate_rental_period:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rental period with this name already exists.")

    for key, value in rental_period.dict(exclude_unset=True).items():
        setattr(db_rental_period, key, value)
    
    db.commit()
    db.refresh(db_rental_period)
    return db_rental_period


@router.delete("/rental-periods/{rental_period_id}", status_code=status.HTTP_200_OK)
def delete_rental_period(rental_period_id: int, db: Session = Depends(get_db)):
    db_rental_period = db.query(RentalPeriod).filter(RentalPeriod.id == rental_period_id).first()
    if db_rental_period is None:
        raise HTTPException(status_code=404, detail="Rental period not found")
    
    db.delete(db_rental_period)
    db.commit()
    return {"detail": "Rental period has been deleted"}