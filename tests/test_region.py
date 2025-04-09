import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.region import Region
from app.schemas.region import RegionCreate

client = TestClient(app)

# Counter for generating unique region codes
_region_counter = 0

import time

@pytest.fixture
def test_region():
    timestamp = int(time.time() * 1000)
    code = f"TEST_{timestamp}"
    
    return {
        "name": f"Test Region {code}",
        "code": code,
        "is_active": True
    }

def test_create_region(test_region):
    response = client.post("/api/regions/", json=test_region)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_region["name"]
    assert data["code"] == test_region["code"]
    assert data["is_active"] == test_region["is_active"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_read_region(test_region):
    # First create a region
    create_response = client.post("/api/regions/", json=test_region)
    created_region = create_response.json()
    
    # Then retrieve it
    response = client.get(f"/api/regions/{created_region['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_region["name"]
    assert data["code"] == test_region["code"]
    assert data["is_active"] == test_region["is_active"]

def test_read_regions(test_region):
    # Create a test region
    client.post("/api/regions/", json=test_region)
    
    response = client.get("/api/regions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert isinstance(data, list)
    assert all(isinstance(region, dict) for region in data)

def test_update_region(test_region):
    # First create a region
    create_response = client.post("/api/regions/", json=test_region)
    created_region = create_response.json()
    
    # Update the region with a unique code
    update_data = {
        "name": "Updated Region",
        "code": f"UPD_{created_region['id']}",
        "is_active": False
    }
    response = client.put(f"/api/regions/{created_region['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["code"] == update_data["code"]
    assert data["is_active"] == update_data["is_active"]

def test_delete_region(test_region):
    # First create a region
    create_response = client.post("/api/regions/", json=test_region)
    created_region = create_response.json()
    
    # Delete the region
    response = client.delete(f"/api/regions/{created_region['id']}")
    assert response.status_code == 204
    
    # Verify the region is deleted
    get_response = client.get(f"/api/regions/{created_region['id']}")
    assert get_response.status_code == 404