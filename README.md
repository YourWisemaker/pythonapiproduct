# Python Product Rental API

A scalable and optimized API that supports product rentals with regional pricing, built with FastAPI and SQLAlchemy. This API allows businesses to manage product catalogs, configure regional pricing, and process rental transactions.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Setup Instructions](#setup-instructions)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Database Setup](#database-setup)
  - [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Product Management**: Create, update, and manage product catalog with custom attributes
- **Regional Pricing**: Configure different prices for the same product based on geographical regions
- **Rental Period Configuration**: Define flexible rental durations (daily, weekly, monthly, etc.)
- **Attribute System**: Add custom attributes to products (size, color, material, etc.)
- **Rental Transaction Processing**: Handle rental bookings, confirmations, cancellations and returns
- **RESTful API**: Well-documented API with standard HTTP methods
- **Input Validation**: Request validation using Pydantic models
- **Interactive Documentation**: Auto-generated Swagger UI for testing and exploration

## Tech Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance web framework for building APIs
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - SQL toolkit and Object-Relational Mapping (ORM)
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation and settings management
- **[Uvicorn](https://www.uvicorn.org/)** - ASGI server implementation
- **[SQLite/PostgreSQL](https://www.postgresql.org/)** - Database (configurable)
- **[Python-Multipart](https://andrew-d.github.io/python-multipart/)** - Parsing multipart form data

## Project Structure

```
.
├── app/                    # Application source code
│   ├── models/             # SQLAlchemy ORM models
│   ├── routers/            # API route handlers
│   ├── schemas/            # Pydantic models for validation
│   ├── database.py         # Database connection and session management
│   └── main.py             # FastAPI application initialization
├── static/                 # Static files for the application
├── tests/                  # Test suite
├── requirements.txt        # Production dependencies
├── requirements-test.txt   # Testing dependencies
├── .env                    # Environment variables (create this file)
└── README.md               # Project documentation
```

## API Endpoints

The API follows RESTful conventions and is organized into the following resource groups:

### Products
- `GET /api/v1/products` - List all products with filtering options
- `GET /api/v1/products/{id}` - Get a specific product with attributes and pricing
- `POST /api/v1/products` - Create a new product
- `PUT /api/v1/products/{id}` - Update an existing product
- `DELETE /api/v1/products/{id}` - Delete a product

### Attributes
- `GET /api/v1/attributes` - List all attributes
- `GET /api/v1/attributes/{id}` - Get a specific attribute
- `POST /api/v1/attributes` - Create a new attribute
- `PUT /api/v1/attributes/{id}` - Update an existing attribute
- `DELETE /api/v1/attributes/{id}` - Delete an attribute

### Attribute Values
- `GET /api/v1/attribute-values` - List all attribute values
- `GET /api/v1/attribute-values/{id}` - Get a specific attribute value
- `POST /api/v1/attribute-values` - Create a new attribute value
- `PUT /api/v1/attribute-values/{id}` - Update an existing attribute value
- `DELETE /api/v1/attribute-values/{id}` - Delete an attribute value

### Regions
- `GET /api/v1/regions` - List all regions
- `GET /api/v1/regions/{id}` - Get a specific region
- `POST /api/v1/regions` - Create a new region
- `PUT /api/v1/regions/{id}` - Update an existing region
- `DELETE /api/v1/regions/{id}` - Delete a region

### Pricing
- `GET /api/v1/pricing` - List all pricing entries
- `GET /api/v1/pricing/{id}` - Get a specific pricing entry
- `POST /api/v1/pricing` - Create a new pricing entry
- `PUT /api/v1/pricing/{id}` - Update an existing pricing entry
- `DELETE /api/v1/pricing/{id}` - Delete a pricing entry

### Rental Periods
- `GET /api/v1/rental-periods` - List all rental periods
- `GET /api/v1/rental-periods/{id}` - Get a specific rental period
- `POST /api/v1/rental-periods` - Create a new rental period
- `PUT /api/v1/rental-periods/{id}` - Update an existing rental period
- `DELETE /api/v1/rental-periods/{id}` - Delete a rental period

### Rental Transactions
- `GET /api/v1/rental-transactions` - List all rental transactions
- `GET /api/v1/rental-transactions/{id}` - Get a specific rental transaction
- `POST /api/v1/rental-transactions` - Create a new rental transaction
- `PUT /api/v1/rental-transactions/{id}` - Update an existing rental transaction
- `DELETE /api/v1/rental-transactions/{id}` - Delete a rental transaction
- `PUT /api/v1/rental-transactions/{id}/status` - Update transaction status

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd pythonapiproduct

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory with the following variables:

```
# For SQLite (default)
DATABASE_URL=sqlite:///./product_rental.db

# For PostgreSQL
# DATABASE_URL=postgresql://user:password@localhost/dbname

SECRET_KEY=your_secret_key
ENVIRONMENT=development
```

### Database Setup

The application automatically creates the database tables when it starts. If you're using migrations:

```bash
# Install alembic if not included in requirements.txt
pip install alembic

# Initialize migrations
alembic init migrations

# Create a migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

### Running the Application

```bash
python -m uvicorn app.main:app --reload
```

By default, the API will be available at http://localhost:8000

You can specify a different port if needed:

```bash
python -m uvicorn app.main:app --reload --port 8003
```

## API Documentation

Once the application is running, you can access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
  - Provides an interactive interface to test API endpoints
  - Shows request/response schemas with examples
  - Includes comprehensive endpoint documentation
  - Displays possible response codes and their meanings

- **Custom Swagger UI**: We've enhanced the default Swagger UI with better organization and documentation

## Testing

The project includes a test suite using pytest. To run the tests:

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Run tests
pytest

# Run tests with coverage report
pytest --cov=app tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.