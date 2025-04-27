"""
Tests for the database models and storage layer
"""
import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from db.storage import Database
from db.models import Unit, ValueDefinition, MeasurementTemplate, Measurement, MeasurementValue
from models.measurement import Unit as UnitSchema
from models.measurement import ValueDefinition as ValueDefinitionSchema
from models.measurement import MeasurementTemplate as MeasurementTemplateSchema
from models.measurement import Measurement as MeasurementSchema
from models.measurement import MeasurementValue as MeasurementValueSchema

def test_create_template(test_db, weight_template):
    """Test creating a measurement template in the database"""
    # Create storage instance
    db = Database(test_db)
    
    # Create template
    result = db.create_template(weight_template)
    
    # Verify result
    assert result.id == weight_template.id
    assert result.name == weight_template.name
    assert len(result.value_definitions) == len(weight_template.value_definitions)
    
    # Verify database state
    templates = db.get_templates()
    assert len(templates) == 1
    assert templates[0].id == weight_template.id

def test_get_template(test_db, weight_template, blood_pressure_template):
    """Test retrieving a specific template from the database"""
    # Create storage instance
    db = Database(test_db)
    
    # Create templates
    db.create_template(weight_template)
    db.create_template(blood_pressure_template)
    
    # Get specific template
    result = db.get_template(weight_template.id)
    
    # Verify result
    assert result is not None
    assert result.id == weight_template.id
    assert result.name == weight_template.name
    
    # Verify non-existent template
    result = db.get_template("non-existent-id")
    assert result is None

def test_create_measurement(test_db, weight_template, weight_measurement):
    """Test creating a measurement in the database"""
    # Create storage instance
    db = Database(test_db)
    
    # Create template first
    db.create_template(weight_template)
    
    # Create measurement
    result = db.create_measurement(weight_measurement)
    
    # Verify result
    assert result.id == weight_measurement.id
    assert result.template_id == weight_measurement.template_id
    assert len(result.values) == len(weight_measurement.values)
    
    # Verify database state
    measurements = db.get_measurements()
    assert len(measurements) == 1
    assert measurements[0].id == weight_measurement.id

def test_get_measurement(test_db, weight_template, weight_measurement, 
                         blood_pressure_template, blood_pressure_measurement):
    """Test retrieving a specific measurement from the database"""
    # Create storage instance
    db = Database(test_db)
    
    # Create templates and measurements
    db.create_template(weight_template)
    db.create_template(blood_pressure_template)
    db.create_measurement(weight_measurement)
    db.create_measurement(blood_pressure_measurement)
    
    # Get specific measurement
    result = db.get_measurement(weight_measurement.id)
    
    # Verify result
    assert result is not None
    assert result.id == weight_measurement.id
    assert result.template_id == weight_measurement.template_id
    
    # Verify non-existent measurement
    result = db.get_measurement("non-existent-id")
    assert result is None

def test_filter_measurements_by_template(test_db, weight_template, weight_measurement, 
                                        blood_pressure_template, blood_pressure_measurement):
    """Test filtering measurements by template"""
    # Create storage instance
    db = Database(test_db)
    
    # Create templates and measurements
    db.create_template(weight_template)
    db.create_template(blood_pressure_template)
    db.create_measurement(weight_measurement)
    db.create_measurement(blood_pressure_measurement)
    
    # Filter by weight template
    results = db.get_measurements(template_id=weight_template.id)
    
    # Verify results
    assert len(results) == 1
    assert results[0].template_id == weight_template.id
    
    # Filter by blood pressure template
    results = db.get_measurements(template_id=blood_pressure_template.id)
    
    # Verify results
    assert len(results) == 1
    assert results[0].template_id == blood_pressure_template.id

def test_filter_measurements_by_date(test_db, weight_template, weight_measurement):
    """Test filtering measurements by date range"""
    # Create storage instance
    db = Database(test_db)
    
    # Create template
    db.create_template(weight_template)
    
    # Create measurements with different dates
    today_measurement = weight_measurement
    db.create_measurement(today_measurement)
    
    # Create a measurement for yesterday
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday_measurement = MeasurementSchema(
        id="yesterday-measurement",
        template_id=weight_template.id,
        values=[
            MeasurementValueSchema(
                definition_name="weight",
                value=74.5
            )
        ],
        measured_at=yesterday,
        recorded_at=yesterday,
        notes="Yesterday's weight",
        user_id="test-user"
    )
    db.create_measurement(yesterday_measurement)
    
    # Create a measurement for last week
    last_week = datetime.utcnow() - timedelta(days=7)
    last_week_measurement = MeasurementSchema(
        id="last-week-measurement",
        template_id=weight_template.id,
        values=[
            MeasurementValueSchema(
                definition_name="weight",
                value=73.5
            )
        ],
        measured_at=last_week,
        recorded_at=last_week,
        notes="Last week's weight",
        user_id="test-user"
    )
    db.create_measurement(last_week_measurement)
    
    # Filter by last 2 days
    start_date = datetime.utcnow() - timedelta(days=2)
    results = db.get_measurements(start_date=start_date)
    
    # Verify results
    assert len(results) == 2
    
    # Filter by last week
    start_date = datetime.utcnow() - timedelta(days=10)
    end_date = datetime.utcnow() - timedelta(days=5)
    results = db.get_measurements(start_date=start_date, end_date=end_date)
    
    # Verify results
    assert len(results) == 1
    assert results[0].id == "last-week-measurement"