from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app.routers import products, attributes, regions, pricing, rental_periods, rental_transactions, attribute_values

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Product Rental API",
    description="A scalable and optimized API that supports product rentals with regional pricing. This API allows you to manage products, their attributes, pricing across different regions, and handle rental transactions.",
    version="1.0.0",
    docs_url=None,  # Disable the default docs
    redoc_url=None,  # Disable the default redoc
    openapi_url="/api/v1/openapi.json",
    terms_of_service="",
    contact={
        "name": "API Support",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add custom schema if needed
    # openapi_schema["info"]["x-logo"] = {"url": "/static/logo.png"}
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Custom Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
        swagger_ui_parameters={
            "docExpansion": "none",
            "defaultModelsExpandDepth": 1,
            "deepLinking": True,
            "displayRequestDuration": True,
        }
    )

# Include routers with enhanced tags
app.include_router(
    products.router, 
    prefix="/api/v1", 
    tags=["Products"]
)
app.include_router(
    attributes.router, 
    prefix="/api/v1", 
    tags=["Attributes"]
)
app.include_router(
    attribute_values.router, 
    prefix="/api/v1", 
    tags=["Attribute Values"]
)
app.include_router(
    regions.router, 
    prefix="/api/v1", 
    tags=["Regions"]
)
app.include_router(
    pricing.router, 
    prefix="/api/v1", 
    tags=["Pricing"]
)
app.include_router(
    rental_periods.router, 
    prefix="/api/v1", 
    tags=["Rental Periods"]
)
app.include_router(
    rental_transactions.router, 
    prefix="/api/v1", 
    tags=["Rental Transactions"]
)

# Root endpoint
@app.get("/", tags=["Root"], summary="API Welcome Endpoint", description="Returns a welcome message for the API")
def read_root():
    """
    Welcome endpoint that confirms the API is running.
    
    Returns:
        dict: A welcome message
    """
    return {"message": "Welcome to the Product Rental API"}