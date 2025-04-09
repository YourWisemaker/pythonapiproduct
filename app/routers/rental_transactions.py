from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models.rental_transaction import RentalTransaction, TransactionStatus
from app.models.product import Product
from app.models.region import Region
from app.models.rental_period import RentalPeriod
from app.models.product_pricing import ProductPricing
from app.schemas.rental_transaction import RentalTransactionCreate, RentalTransactionUpdate, RentalTransactionResponse, RentalTransactionDetailResponse, RentalTransactionCheck, RentalTransactionCheckResponse

router = APIRouter()


@router.post("/rental-transactions", response_model=RentalTransactionResponse, status_code=status.HTTP_201_CREATED)
def create_rental_transaction(transaction: RentalTransactionCreate, db: Session = Depends(get_db)):
    # Verify that product, region, and rental period exist
    product = db.query(Product).filter(Product.id == transaction.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    region = db.query(Region).filter(Region.id == transaction.region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    
    rental_period = db.query(RentalPeriod).filter(RentalPeriod.id == transaction.rental_period_id).first()
    if not rental_period:
        raise HTTPException(status_code=404, detail="Rental period not found")
    
    # Validate dates
    if transaction.start_date >= transaction.end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Check if product is already rented for the requested period
    overlapping_transactions = db.query(RentalTransaction).filter(
        RentalTransaction.product_id == transaction.product_id,
        RentalTransaction.status == TransactionStatus.CONFIRMED,
        RentalTransaction.start_date <= transaction.end_date,
        RentalTransaction.end_date >= transaction.start_date
    ).all()
    
    if overlapping_transactions:
        raise HTTPException(
            status_code=400, 
            detail="Product is already rented for the requested period"
        )
    
    db_transaction = RentalTransaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/rental-transactions", response_model=List[RentalTransactionResponse])
def read_rental_transactions(
    skip: int = 0, 
    limit: int = 100, 
    product_id: Optional[int] = None,
    region_id: Optional[int] = None,
    rental_period_id: Optional[int] = None,
    customer_email: Optional[str] = None,
    status: Optional[TransactionStatus] = None,
    start_date_from: Optional[datetime] = None,
    start_date_to: Optional[datetime] = None,
    end_date_from: Optional[datetime] = None,
    end_date_to: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(RentalTransaction)
    
    if product_id:
        query = query.filter(RentalTransaction.product_id == product_id)
    
    if region_id:
        query = query.filter(RentalTransaction.region_id == region_id)
    
    if rental_period_id:
        query = query.filter(RentalTransaction.rental_period_id == rental_period_id)
    
    if customer_email:
        query = query.filter(RentalTransaction.customer_email.ilike(f"%{customer_email}%"))
    
    if status:
        query = query.filter(RentalTransaction.status == status)
    
    if start_date_from:
        query = query.filter(RentalTransaction.start_date >= start_date_from)
    
    if start_date_to:
        query = query.filter(RentalTransaction.start_date <= start_date_to)
    
    if end_date_from:
        query = query.filter(RentalTransaction.end_date >= end_date_from)
    
    if end_date_to:
        query = query.filter(RentalTransaction.end_date <= end_date_to)
    
    return query.order_by(RentalTransaction.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/rental-transactions/{transaction_id}", response_model=RentalTransactionDetailResponse)
def read_rental_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = db.query(RentalTransaction).filter(RentalTransaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Rental transaction not found")
    
    # Create response with nested data
    response = RentalTransactionDetailResponse(
        id=db_transaction.id,
        product_id=db_transaction.product_id,
        region_id=db_transaction.region_id,
        rental_period_id=db_transaction.rental_period_id,
        customer_name=db_transaction.customer_name,
        customer_email=db_transaction.customer_email,
        customer_address=db_transaction.customer_address,
        start_date=db_transaction.start_date,
        end_date=db_transaction.end_date,
        price=db_transaction.price,
        status=db_transaction.status,
        notes=db_transaction.notes,
        created_at=db_transaction.created_at,
        updated_at=db_transaction.updated_at,
        product={
            "id": db_transaction.product.id,
            "name": db_transaction.product.name,
            "sku": db_transaction.product.sku
        },
        region={
            "id": db_transaction.region.id,
            "name": db_transaction.region.name,
            "code": db_transaction.region.code
        },
        rental_period={
            "id": db_transaction.rental_period.id,
            "name": db_transaction.rental_period.name,
            "days": db_transaction.rental_period.days
        }
    )
    
    return response


@router.put("/rental-transactions/{transaction_id}", response_model=RentalTransactionResponse)
def update_rental_transaction(transaction_id: int, transaction: RentalTransactionUpdate, db: Session = Depends(get_db)):
    db_transaction = db.query(RentalTransaction).filter(RentalTransaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Rental transaction not found")
    
    update_data = transaction.dict(exclude_unset=True)
    
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
    
    # Validate dates if updating
    start_date = update_data.get("start_date", db_transaction.start_date)
    end_date = update_data.get("end_date", db_transaction.end_date)
    
    if start_date >= end_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")
    
    # Check for overlapping rentals if changing dates or product
    if ("start_date" in update_data or "end_date" in update_data or "product_id" in update_data) and \
       (update_data.get("status", db_transaction.status) == TransactionStatus.CONFIRMED):
        
        product_id = update_data.get("product_id", db_transaction.product_id)
        
        overlapping_transactions = db.query(RentalTransaction).filter(
            RentalTransaction.product_id == product_id,
            RentalTransaction.status == TransactionStatus.CONFIRMED,
            RentalTransaction.id != transaction_id,
            RentalTransaction.start_date <= end_date,
            RentalTransaction.end_date >= start_date
        ).all()
        
        if overlapping_transactions:
            raise HTTPException(
                status_code=400, 
                detail="Product is already rented for the requested period"
            )
    
    for key, value in update_data.items():
        setattr(db_transaction, key, value)
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/rental-transactions/{transaction_id}", status_code=status.HTTP_200_OK)
def delete_rental_transaction(transaction_id: int, db: Session = Depends(get_db)):
    db_transaction = db.query(RentalTransaction).filter(RentalTransaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(db_transaction)
    db.commit()
    return {"detail": "Rental transaction has been deleted"}


@router.put("/rental-transactions/{transaction_id}/status", response_model=RentalTransactionResponse)
def update_transaction_status(
    transaction_id: int, 
    status: TransactionStatus, 
    db: Session = Depends(get_db)
):
    db_transaction = db.query(RentalTransaction).filter(RentalTransaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Rental transaction not found")
    
    db_transaction.status = status
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.post("/check-rental", response_model=RentalTransactionCheckResponse)
async def check_rental_transaction(check: RentalTransactionCheck = Body(...), db: Session = Depends(get_db)):
    """Check if a product is available for rental based on pricing_id and date range"""
    # 1. Verify that pricing exists and retrieve its information
    pricing = db.query(ProductPricing).filter(ProductPricing.id == check.pricing_id).first()
    if not pricing:
        return RentalTransactionCheckResponse(
            available=False,
            message="Pricing not found"
        )
    
    # 2. Verify that the pricing matches the provided product, region, and rental period
    if (pricing.product_id != check.product_id or 
        pricing.region_id != check.region_id or 
        pricing.rental_period_id != check.rental_period_id):
        return RentalTransactionCheckResponse(
            available=False,
            message="Pricing does not match the provided product, region, and rental period"
        )
    
    # 3. Check if pricing is active
    if not pricing.is_active:
        return RentalTransactionCheckResponse(
            available=False,
            message="Pricing is not active for this product, region, and rental period"
        )
    
    # 4. Set default dates if not provided
    start_date = check.start_date or datetime.now()
    
    # Get rental period days if end_date isn't provided
    if not check.end_date:
        rental_period = db.query(RentalPeriod).filter(RentalPeriod.id == check.rental_period_id).first()
        if not rental_period:
            return RentalTransactionCheckResponse(
                available=False,
                message="Rental period not found"
            )
        end_date = start_date + timedelta(days=rental_period.days)
    else:
        end_date = check.end_date
    
    # 5. Check if the dates are valid
    if start_date >= end_date:
        return RentalTransactionCheckResponse(
            available=False,
            message="End date must be after start date"
        )
    
    # 6. Check if product is available for the requested period
    overlapping_transactions = db.query(RentalTransaction).filter(
        RentalTransaction.product_id == check.product_id,
        RentalTransaction.status == TransactionStatus.CONFIRMED,
        RentalTransaction.start_date <= end_date,
        RentalTransaction.end_date >= start_date
    ).all()
    
    if overlapping_transactions:
        return RentalTransactionCheckResponse(
            available=False,
            message="Product is already rented for the requested period"
        )
    
    # 7. Get information about related entities for the response
    product = db.query(Product).filter(Product.id == check.product_id).first()
    region = db.query(Region).filter(Region.id == check.region_id).first()
    rental_period = db.query(RentalPeriod).filter(RentalPeriod.id == check.rental_period_id).first()
    
    # 8. Return success response
    return RentalTransactionCheckResponse(
        available=True,
        product={
            "id": product.id,
            "name": product.name,
            "sku": product.sku
        },
        region={
            "id": region.id,
            "name": region.name,
            "code": region.code
        },
        rental_period={
            "id": rental_period.id,
            "name": rental_period.name,
            "days": rental_period.days
        },
        pricing={
            "id": pricing.id,
            "price": float(pricing.price) if pricing.price else None
        },
        message="Product is available for rental during the requested period"
    )