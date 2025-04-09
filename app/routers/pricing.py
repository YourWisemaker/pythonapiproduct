from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.database import get_db
from app.models.product_pricing import ProductPricing
from app.models.product import Product
from app.models.region import Region
from app.models.rental_period import RentalPeriod
from app.schemas.product_pricing import ProductPricingCreate, ProductPricingUpdate, ProductPricingResponse, ProductPricingDetailResponse

router = APIRouter()


@router.post("/pricing", response_model=ProductPricingResponse, status_code=status.HTTP_201_CREATED)
def create_pricing(pricing: ProductPricingCreate, db: Session = Depends(get_db)):
    # Verify that product, region, and rental period exist
    product = db.query(Product).filter(Product.id == pricing.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    region = db.query(Region).filter(Region.id == pricing.region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    rental_period = db.query(RentalPeriod).filter(RentalPeriod.id == pricing.rental_period_id).first()
    if not rental_period:
        raise HTTPException(status_code=404, detail="Rental period not found")
    
    # Check if pricing already exists for this combination
    existing_pricing = db.query(ProductPricing).filter(
        ProductPricing.product_id == pricing.product_id,
        ProductPricing.region_id == pricing.region_id,
        ProductPricing.rental_period_id == pricing.rental_period_id
    ).first()
    
    if existing_pricing:
        raise HTTPException(
            status_code=400, 
            detail="Pricing already exists for this product, region, and rental period combination"
        )
    
    db_pricing = ProductPricing(**pricing.dict())
    db.add(db_pricing)
    db.commit()
    db.refresh(db_pricing)
    return db_pricing


@router.get("/pricing", response_model=List[ProductPricingResponse])
def read_pricing(
    skip: int = 0, 
    limit: int = 100, 
    product_id: Optional[int] = None,
    region_id: Optional[int] = None,
    rental_period_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ProductPricing)
    
    if product_id:
        query = query.filter(ProductPricing.product_id == product_id)
    
    if region_id:
        query = query.filter(ProductPricing.region_id == region_id)
    
    if rental_period_id:
        query = query.filter(ProductPricing.rental_period_id == rental_period_id)
    
    if min_price is not None:
        query = query.filter(ProductPricing.price >= min_price)
    
    if max_price is not None:
        query = query.filter(ProductPricing.price <= max_price)
    
    if is_active is not None:
        query = query.filter(ProductPricing.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/pricing/{pricing_id}", response_model=ProductPricingDetailResponse)
def read_pricing_detail(pricing_id: int, db: Session = Depends(get_db)):
    db_pricing = db.query(ProductPricing).filter(ProductPricing.id == pricing_id).first()
    if db_pricing is None:
        raise HTTPException(status_code=404, detail="Pricing not found")
    
    # Create response with nested data
    response = ProductPricingDetailResponse(
        id=db_pricing.id,
        product_id=db_pricing.product_id,
        region_id=db_pricing.region_id,
        rental_period_id=db_pricing.rental_period_id,
        price=db_pricing.price,
        is_active=db_pricing.is_active,
        created_at=db_pricing.created_at,
        updated_at=db_pricing.updated_at,
        product={
            "id": db_pricing.product.id,
            "name": db_pricing.product.name,
            "sku": db_pricing.product.sku
        },
        region={
            "id": db_pricing.region.id,
            "name": db_pricing.region.name,
            "code": db_pricing.region.code
        },
        rental_period={
            "id": db_pricing.rental_period.id,
            "name": db_pricing.rental_period.name,
            "days": db_pricing.rental_period.days
        }
    )
    
    return response


@router.put("/pricing/{pricing_id}", response_model=ProductPricingResponse)
def update_pricing(pricing_id: int, pricing: ProductPricingUpdate, db: Session = Depends(get_db)):
    db_pricing = db.query(ProductPricing).filter(ProductPricing.id == pricing_id).first()
    if db_pricing is None:
        raise HTTPException(status_code=404, detail="Pricing not found")
    
    update_data = pricing.dict(exclude_unset=True)
    
    # If updating product, region, or rental period, verify they exist
    if "product_id" in update_data:
        product = db.query(Product).filter(Product.id == update_data["product_id"]).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
    
    if "region_id" in update_data:
        region = db.query(Region).filter(Region.id == update_data["region_id"]).first()
        if not region:
            raise HTTPException(status_code=404, detail="Region not found")
    
    if "rental_period_id" in update_data:
        rental_period = db.query(RentalPeriod).filter(RentalPeriod.id == update_data["rental_period_id"]).first()
        if not rental_period:
            raise HTTPException(status_code=404, detail="Rental period not found")
    
    # Check if updating to a combination that already exists
    product_id = update_data.get("product_id", db_pricing.product_id)
    region_id = update_data.get("region_id", db_pricing.region_id)
    rental_period_id = update_data.get("rental_period_id", db_pricing.rental_period_id)
    
    existing_pricing = db.query(ProductPricing).filter(
        ProductPricing.product_id == product_id,
        ProductPricing.region_id == region_id,
        ProductPricing.rental_period_id == rental_period_id,
        ProductPricing.id != pricing_id
    ).first()
    
    if existing_pricing:
        raise HTTPException(
            status_code=400, 
            detail="Pricing already exists for this product, region, and rental period combination"
        )
    
    for key, value in update_data.items():
        setattr(db_pricing, key, value)
    
    db.commit()
    db.refresh(db_pricing)
    return db_pricing


@router.delete("/pricing/{pricing_id}", status_code=status.HTTP_200_OK)
def delete_pricing(pricing_id: int, db: Session = Depends(get_db)):
    db_pricing = db.query(ProductPricing).filter(ProductPricing.id == pricing_id).first()
    if db_pricing is None:
        raise HTTPException(status_code=404, detail="Pricing not found")
    
    db.delete(db_pricing)
    db.commit()
    return {"detail": "Pricing has been deleted"}