from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductDetailResponse
from app.models.product_attribute_value import ProductAttributeValue

router = APIRouter()


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Check for duplicate product name
    existing_product = db.query(Product).filter(Product.name == product.name).first()
    if existing_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product with this name already exists.")
    
    # Check for duplicate SKU
    existing_sku = db.query(Product).filter(Product.sku == product.sku).first()
    if existing_sku:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product with this SKU already exists.")
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


@router.get("/products", response_model=List[ProductResponse])
def read_products(
    skip: int = 0, 
    limit: int = 100, 
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get("/products/{product_id}", response_model=ProductDetailResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get attribute values with their attribute information
    attribute_values = []
    for pav in db_product.attribute_values:
        av = pav.attribute_value
        attribute_values.append({
            "id": av.id,
            "attribute": {
                "id": av.attribute.id,
                "name": av.attribute.name,
                "type": av.attribute.type
            },
            "value": av.value
        })
    
    # Get pricing information
    pricing = []
    for price in db_product.pricing:
        pricing.append({
            "id": price.id,
            "region": {
                "id": price.region.id,
                "name": price.region.name,
                "code": price.region.code
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
    response = ProductDetailResponse(
        id=db_product.id,
        name=db_product.name,
        description=db_product.description,
        sku=db_product.sku,
        is_active=db_product.is_active,
        created_at=db_product.created_at,
        updated_at=db_product.updated_at,
        attribute_values=attribute_values,
        pricing=pricing
    )
    
    return response


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check for duplicate product name
    duplicate_product = db.query(Product).filter(Product.name == product.name, Product.id != product_id).first()
    if duplicate_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product with this name already exists.")
    
    # Check for duplicate SKU
    duplicate_sku = db.query(Product).filter(Product.sku == product.sku, Product.id != product_id).first()
    if duplicate_sku:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product with this SKU already exists.")

    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/products/{product_id}", status_code=status.HTTP_200_OK)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    try:
        db.delete(db_product)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to delete product. It may be referenced elsewhere.")
    return {"detail": "Product has been deleted"}