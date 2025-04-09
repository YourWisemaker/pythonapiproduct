# Python API Product

A scalable and optimized API that supports product rentals with regional pricing, built with FastAPI and SQLAlchemy. This is a Python port of the Laravel Product Rental API.

## Features

- Product management with attributes
- Regional pricing
- Rental period configuration
- Rental transaction processing
- RESTful API endpoints

## Tech Stack

- FastAPI - High-performance web framework
- SQLAlchemy - SQL toolkit and ORM
- Pydantic - Data validation and settings management
- Alembic - Database migration tool
- PostgreSQL - Database (configurable)

## Setup Instructions

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
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key
ENVIRONMENT=development
```

### Database Setup

```bash
# Run migrations
alembic upgrade head
```

### Running the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### API Documentation

Once the application is running, you can access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc