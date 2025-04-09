from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the parent directory to the path so we can import the app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the necessary models
from app.models.product_pricing import ProductPricing
from app.models.product import Product
from app.models.region import Region
from app.models.rental_period import RentalPeriod
from app.database import engine

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Query all pricing records with related information
pricing_records = session.query(
    ProductPricing, 
    Product.name.label("product_name"),
    Region.name.label("region_name"),
    RentalPeriod.name.label("period_name")
).join(
    Product, ProductPricing.product_id == Product.id
).join(
    Region, ProductPricing.region_id == Region.id
).join(
    RentalPeriod, ProductPricing.rental_period_id == RentalPeriod.id
).all()

# Print table header
print(f"\n{'ID':<5} {'Product ID':<12} {'Product':<20} {'Region ID':<10} {'Region':<15} {'Period ID':<10} {'Period':<15} {'Price':<10} {'Active':<8}")
print("-" * 110)

# Print pricing records
for record in pricing_records:
    pricing, product_name, region_name, period_name = record
    print(f"{pricing.id:<5} {pricing.product_id:<12} {product_name:<20} {pricing.region_id:<10} {region_name:<15} {pricing.rental_period_id:<10} {period_name:<15} {pricing.price:<10} {pricing.is_active}")

print(f"\nTotal pricing records: {len(pricing_records)}")

# Close the session
session.close()
