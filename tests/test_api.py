"""
Tests for the API endpoints
"""
import pytest
from fastapi.testclient import TestClient
import json
from datetime import datetime, timedelta

def test_root_endpoint(client):
    """Test the root endpoint returns a welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Life Measurements Tracker API"}

def test_create_template(client, weight_template):
    """Test creating a template via the API"""
    # Convert template to dict
    template_dict = weight_template.dict()
    
    # Send request
    response = client.post("/templates", json=template_dict)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == weight_template.id
    assert result["name"] == weight_template.name
    assert len(result["value_definitions"]) == len(weight_template.value_definitions)

def test_get_templates(client, weight_template, blood_pressure_template):
    """Test retrieving all templates via the API"""
    # Create templates
    client.post("/templates", json=weight_template.dict())
    client.post("/templates", json=blood_pressure_template.dict())
    
    # Get templates
    response = client.get("/templates")
    
    # Verify response
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    assert results[0]["id"] in [weight_template.id, blood_pressure_template.id]
    assert results[1]["id"] in [weight_template.id, blood_pressure_template.id]
    assert results[0]["id"] != results[1]["id"]

def test_get_specific_template(client, weight_template):
    """Test retrieving a specific template via the API"""
    # Create template
    client.post("/templates", json=weight_template.dict())
    
    # Get specific template
    response = client.get(f"/templates/{weight_template.id}")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == weight_template.id
    assert result["name"] == weight_template.name
    
    # Test non-existent template
    response = client.get("/templates/non-existent-id")
    assert response.status_code == 404

def test_create_measurement(client, weight_template, weight_measurement):
    """Test creating a measurement via the API"""
    # Create template first
    client.post("/templates", json=weight_template.dict())
    
    # Convert measurement to dict
    measurement_dict = weight_measurement.dict()
    
    # Send request
    response = client.post("/measurements", json=measurement_dict)
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == weight_measurement.id
    assert result["template_id"] == weight_measurement.template_id
    assert len(result["values"]) == len(weight_measurement.values)

def test_get_measurements(client, weight_template, weight_measurement,
                         blood_pressure_template, blood_pressure_measurement):
    """Test retrieving all measurements via the API"""
    # Create templates
    client.post("/templates", json=weight_template.dict())
    client.post("/templates", json=blood_pressure_template.dict())
    
    # Create measurements
    client.post("/measurements", json=weight_measurement.dict())
    client.post("/measurements", json=blood_pressure_measurement.dict())
    
    # Get all measurements
    response = client.get("/measurements")
    
    # Verify response
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 2
    
    # Get measurements filtered by template
    response = client.get(f"/measurements?template_id={weight_template.id}")
    
    # Verify response
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["template_id"] == weight_template.id

def test_get_specific_measurement(client, weight_template, weight_measurement):
    """Test retrieving a specific measurement via the API"""
    # Create template and measurement
    client.post("/templates", json=weight_template.dict())
    client.post("/measurements", json=weight_measurement.dict())
    
    # Get specific measurement
    response = client.get(f"/measurements/{weight_measurement.id}")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == weight_measurement.id
    assert result["template_id"] == weight_template.id
    
    # Test non-existent measurement
    response = client.get("/measurements/non-existent-id")
    assert response.status_code == 404

def test_statistics(client, weight_template, weight_measurement):
    """Test the statistics endpoint"""
    # Create template
    client.post("/templates", json=weight_template.dict())
    
    # Create multiple measurements with different weights
    measurement1 = weight_measurement.dict()
    measurement1["values"][0]["value"] = 70.0
    client.post("/measurements", json=measurement1)
    
    measurement2 = weight_measurement.dict()
    measurement2["id"] = "measurement-2"
    measurement2["values"][0]["value"] = 72.0
    client.post("/measurements", json=measurement2)
    
    measurement3 = weight_measurement.dict()
    measurement3["id"] = "measurement-3"
    measurement3["values"][0]["value"] = 74.0
    client.post("/measurements", json=measurement3)
    
    # Get statistics
    response = client.get(f"/statistics/{weight_template.id}")
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert "weight" in result
    assert result["weight"]["count"] == 3
    assert result["weight"]["min"] == 70.0
    assert result["weight"]["max"] == 74.0
    assert result["weight"]["avg"] == 72.0
    assert result["weight"]["unit"] == "kg"