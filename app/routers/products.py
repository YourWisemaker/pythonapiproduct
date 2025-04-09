from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductDetailResponse
from app.models.product_attribute_value import ProductAttributeValue

router = APIRouter()


@router.post(
    "/products", 
    response_model=ProductResponse, 
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    description="Creates a new product in the system with the provided details.",
    responses={
        201: {"description": "Product created successfully"},
        400: {"description": "Bad request - Product with this name or SKU already exists"}
    }
)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """
    Create a new product with the provided details.
    
    Args:
        product: Product data including name, description, and SKU
        db: Database session dependency
        
    Returns:
        ProductResponse: The newly created product
        
    Raises:
        HTTPException: If a product with the same name or SKU already exists
    """
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


@router.get(
    "/products", 
    response_model=List[ProductResponse],
    summary="Get all products",
    description="Retrieve a list of products with optional filtering.",
    responses={
        200: {"description": "List of products retrieved successfully"}
    }
)
def read_products(
    skip: int = 0, 
    limit: int = 100, 
    name: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of products with optional filtering.
    
    Args:
        skip: Number of products to skip (pagination)
        limit: Maximum number of products to return (pagination)
        name: Optional filter for product name (partial match)
        is_active: Optional filter for active status
        db: Database session dependency
        
    Returns:
        List[ProductResponse]: List of products matching the criteria
    """
    query = db.query(Product)
    
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


@router.get(
    "/products/{product_id}", 
    response_model=ProductDetailResponse,
    summary="Get a specific product by ID",
    description="Retrieve detailed information about a specific product by its ID.",
    responses={
        200: {"description": "Product details retrieved successfully"},
        404: {"description": "Product not found"}
    }
)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed information about a specific product by its ID.
    
    Args:
        product_id: ID of the product to retrieve
        db: Database session dependency
        
    Returns:
        ProductDetailResponse: Detailed product information including attributes and pricing
        
    Raises:
        HTTPException: If the product is not found
    """
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


@router.put(
    "/products/{product_id}", 
    response_model=ProductResponse,
    summary="Update a product",
    description="Update an existing product with the provided details.",
    responses={
        200: {"description": "Product updated successfully"},
        400: {"description": "Bad request - Product with this name or SKU already exists"},
        404: {"description": "Product not found"}
    }
)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    """
    Update an existing product with the provided details.
    
    Args:
        product_id: ID of the product to update
        product: Updated product data
        db: Database session dependency
        
    Returns:
        ProductResponse: The updated product
        
    Raises:
        HTTPException: If the product is not found or if there's a duplicate name/SKU
    """
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


@router.delete(
    "/products/{product_id}", 
    status_code=status.HTTP_200_OK,
    summary="Delete a product",
    description="Delete a product from the system by its ID.",
    responses={
        200: {"description": "Product deleted successfully"},
        400: {"description": "Bad request - Product cannot be deleted as it is referenced elsewhere"},
        404: {"description": "Product not found"}
    }
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """
    Delete a product from the system by its ID.
    
    Args:
        product_id: ID of the product to delete
        db: Database session dependency
        
    Returns:
        dict: Confirmation message
        
    Raises:
        HTTPException: If the product is not found or cannot be deleted
    """
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