"""
Test fixtures and utilities
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from api.main import app
from tests.test_config import TestSessionLocal, setup_test_db, teardown_test_db
from db.storage import Database
from models.measurement import MeasurementTemplate, ValueDefinition, Unit, Measurement, MeasurementValue

# Override the get_db dependency
def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the get_storage dependency
def override_get_storage():
    db = next(override_get_db())
    return Database(db)

# Setup and teardown for each test
@pytest.fixture(scope="function")
def test_db():
    # Setup database
    setup_test_db()
    
    # Provide the database session
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
    
    # Teardown database
    teardown_test_db()

# Test client with overridden dependencies
@pytest.fixture(scope="function")
def client(test_db):
    # Override dependencies
    from db.database import get_db
    from db.storage import get_storage
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_storage] = override_get_storage
    
    # Create test client
    with TestClient(app) as client:
        yield client
    
    # Reset dependency overrides
    app.dependency_overrides = {}

# Sample data fixtures
@pytest.fixture
def weight_template():
    return MeasurementTemplate(
        id=str(uuid.uuid4()),
        name="Weight",
        description="Daily weight measurement",
        value_definitions=[
            ValueDefinition(
                name="weight",
                display_name="Weight",
                unit=Unit(
                    name="kg",
                    display_name="kilogram"
                ),
                min_value=0,
                max_value=500
            )
        ],
        created_at=datetime.utcnow(),
        is_active=True
    )

@pytest.fixture
def blood_pressure_template():
    return MeasurementTemplate(
        id=str(uuid.uuid4()),
        name="Blood Pressure",
        description="Blood pressure measurement",
        value_definitions=[
            ValueDefinition(
                name="systolic",
                display_name="Systolic",
                unit=Unit(
                    name="mmHg",
                    display_name="millimeters of mercury"
                ),
                min_value=0,
                max_value=300
            ),
            ValueDefinition(
                name="diastolic",
                display_name="Diastolic",
                unit=Unit(
                    name="mmHg",
                    display_name="millimeters of mercury"
                ),
                min_value=0,
                max_value=200
            ),
            ValueDefinition(
                name="pulse",
                display_name="Pulse",
                unit=Unit(
                    name="bpm",
                    display_name="beats per minute"
                ),
                min_value=0,
                max_value=250
            )
        ],
        created_at=datetime.utcnow(),
        is_active=True
    )

@pytest.fixture
def weight_measurement(weight_template):
    return Measurement(
        id=str(uuid.uuid4()),
        template_id=weight_template.id,
        values=[
            MeasurementValue(
                definition_name="weight",
                value=75.5
            )
        ],
        measured_at=datetime.utcnow(),
        recorded_at=datetime.utcnow(),
        notes="Morning weight",
        user_id="test-user"
    )

@pytest.fixture
def blood_pressure_measurement(blood_pressure_template):
    return Measurement(
        id=str(uuid.uuid4()),
        template_id=blood_pressure_template.id,
        values=[
            MeasurementValue(
                definition_name="systolic",
                value=120.0
            ),
            MeasurementValue(
                definition_name="diastolic",
                value=80.0
            ),
            MeasurementValue(
                definition_name="pulse",
                value=72.0
            )
        ],
        measured_at=datetime.utcnow(),
        recorded_at=datetime.utcnow(),
        notes="Morning blood pressure",
        user_id="test-user"
    )