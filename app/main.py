from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.routers import products, attributes, regions, pricing, rental_periods, rental_transactions, attribute_values

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Rental API",
    description="A scalable and optimized API that supports product rentals with regional pricing",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/v1", tags=["Products"])
app.include_router(attributes.router, prefix="/api/v1", tags=["Attributes"])
app.include_router(attribute_values.router, prefix="/api/v1", tags=["Attribute Values"])
app.include_router(regions.router, prefix="/api/v1", tags=["Regions"])
app.include_router(pricing.router, prefix="/api/v1", tags=["Pricing"])
app.include_router(rental_periods.router, prefix="/api/v1", tags=["Rental Periods"])
app.include_router(rental_transactions.router, prefix="/api/v1", tags=["Rental Transactions"])


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Product Rental API"}