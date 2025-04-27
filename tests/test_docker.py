"""
Tests for Docker container configuration
Note: These tests assume Docker and Docker Compose are installed and available.
"""
import pytest
import subprocess
import time
import requests
import os
import sys

# Skip these tests if running in CI/CD environment or if docker is not available
docker_available = False
try:
    subprocess.run(["docker", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    docker_available = True
except (subprocess.CalledProcessError, FileNotFoundError):
    docker_available = False

# Mark the entire module to be skipped if Docker is not available
pytestmark = pytest.mark.skipif(
    not docker_available or "CI" in os.environ,
    reason="Docker tests are only run locally and when Docker is available"
)

@pytest.fixture(scope="module")
def docker_compose_setup():
    """Set up Docker Compose environment for testing"""
    try:
        # Stop any existing containers
        subprocess.run(
            ["docker", "compose", "down", "-v"], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Start containers
        subprocess.run(
            ["docker", "compose", "up", "-d"], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        # Wait for containers to be ready
        time.sleep(10)
        
        # Yield control back to the test
        yield
    finally:
        # Clean up
        subprocess.run(
            ["docker", "compose", "down", "-v"], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

def test_api_container(docker_compose_setup):
    """Test that the API container is running and accessible"""
    response = requests.get("http://localhost:8000")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Life Measurements Tracker API"}

def test_web_container(docker_compose_setup):
    """Test that the web container is running and accessible"""
    response = requests.get("http://localhost:8080")
    assert response.status_code == 200
    assert "Life Measurements Tracker" in response.text

def test_postgres_container(docker_compose_setup):
    """Test that the postgres container is running and the API can access the database"""
    # Check that we can access templates endpoint
    response = requests.get("http://localhost:8000/templates")
    assert response.status_code == 200
    
    # Create a template
    template = {
        "id": "test-docker-template",
        "name": "Docker Test",
        "description": "Template for testing Docker setup",
        "value_definitions": [
            {
                "name": "test_value",
                "display_name": "Test Value",
                "unit": {
                    "name": "unit",
                    "display_name": "Test Unit"
                }
            }
        ],
        "created_at": "2025-04-23T12:00:00Z",
        "is_active": True
    }
    
    response = requests.post("http://localhost:8000/templates", json=template)
    assert response.status_code == 200
    
    # Check that template was created
    response = requests.get("http://localhost:8000/templates/test-docker-template")
    assert response.status_code == 200
    assert response.json()["name"] == "Docker Test"