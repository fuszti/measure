"""
Tests for the data migration from JSON to PostgreSQL
"""
import pytest
import os
import json
import tempfile
from datetime import datetime
import uuid

from db.migrate_data import migrate_data, load_json_file
from db.storage import Database

def test_load_json_file():
    """Test loading data from a JSON file"""
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
        json.dump([{"id": "test", "name": "Test"}], f)
        temp_file = f.name
    
    try:
        # Load file
        data = load_json_file(temp_file)
        
        # Verify data
        assert data is not None
        assert len(data) == 1
        assert data[0]["id"] == "test"
        assert data[0]["name"] == "Test"
        
        # Test loading non-existent file
        data = load_json_file("non-existent-file.json")
        assert data == []
    finally:
        # Clean up
        os.unlink(temp_file)

def test_migration(test_db):
    """Test migration from JSON files to the database"""
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create sample templates JSON
        templates = [
            {
                "id": str(uuid.uuid4()),
                "name": "Weight",
                "description": "Weight measurement",
                "value_definitions": [
                    {
                        "name": "weight",
                        "display_name": "Weight",
                        "unit": {
                            "name": "kg",
                            "display_name": "kilogram"
                        },
                        "min_value": 0,
                        "max_value": 500
                    }
                ],
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
        ]
        
        # Create sample measurements JSON
        measurements = [
            {
                "id": str(uuid.uuid4()),
                "template_id": templates[0]["id"],
                "values": [
                    {
                        "definition_name": "weight",
                        "value": 75.5
                    }
                ],
                "measured_at": datetime.utcnow().isoformat(),
                "recorded_at": datetime.utcnow().isoformat(),
                "notes": "Test measurement",
                "user_id": "test-user"
            }
        ]
        
        # Write JSON files
        with open(os.path.join(temp_dir, "templates.json"), 'w') as f:
            json.dump(templates, f)
        
        with open(os.path.join(temp_dir, "measurements.json"), 'w') as f:
            json.dump(measurements, f)
        
        # Run migration
        migrate_data(temp_dir)
        
        # Verify database state
        db = Database(test_db)
        
        # Check templates
        db_templates = db.get_templates()
        assert len(db_templates) == 1
        assert db_templates[0].id == templates[0]["id"]
        assert db_templates[0].name == templates[0]["name"]
        
        # Check measurements
        db_measurements = db.get_measurements()
        assert len(db_measurements) == 1
        assert db_measurements[0].template_id == templates[0]["id"]
        assert len(db_measurements[0].values) == 1
        assert db_measurements[0].values[0].definition_name == "weight"
        assert db_measurements[0].values[0].value == 75.5
    finally:
        # Clean up
        for filename in os.listdir(temp_dir):
            os.unlink(os.path.join(temp_dir, filename))
        os.rmdir(temp_dir)