import json
import os
from datetime import datetime
import uuid
from typing import List, Dict, Any

from sqlalchemy.orm import Session
from db.database import SessionLocal, engine, Base
from db.models import Unit, ValueDefinition, MeasurementTemplate, Measurement, MeasurementValue

def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """Load data from a JSON file."""
    if not os.path.exists(file_path):
        return []
        
    with open(file_path, 'r') as f:
        return json.load(f)

def migrate_templates(templates_data: List[Dict[str, Any]], db: Session) -> None:
    """Migrate template data from JSON to PostgreSQL."""
    for template_data in templates_data:
        # Create template
        template = MeasurementTemplate(
            id=template_data.get('id', str(uuid.uuid4())),
            name=template_data.get('name', ''),
            description=template_data.get('description'),
            created_at=datetime.fromisoformat(template_data.get('created_at')) if isinstance(template_data.get('created_at'), str) else template_data.get('created_at', datetime.utcnow()),
            updated_at=datetime.fromisoformat(template_data.get('updated_at')) if isinstance(template_data.get('updated_at'), str) else template_data.get('updated_at'),
            is_active=template_data.get('is_active', True),
            owner_id=template_data.get('owner_id')
        )
        
        db.add(template)
        db.flush()  # Get the ID
        
        # Create value definitions and units
        for value_def_data in template_data.get('value_definitions', []):
            unit_data = value_def_data.get('unit', {})
            
            # Look for existing unit
            unit = db.query(Unit).filter(Unit.name == unit_data.get('name')).first()
            
            if not unit:
                unit = Unit(
                    name=unit_data.get('name', ''),
                    display_name=unit_data.get('display_name', ''),
                    description=unit_data.get('description')
                )
                db.add(unit)
                db.flush()
            
            # Create value definition
            value_def = ValueDefinition(
                name=value_def_data.get('name', ''),
                display_name=value_def_data.get('display_name', ''),
                description=value_def_data.get('description'),
                unit_id=unit.id,
                min_value=value_def_data.get('min_value'),
                max_value=value_def_data.get('max_value'),
                template_id=template.id
            )
            
            db.add(value_def)
    
    db.commit()

def migrate_measurements(measurements_data: List[Dict[str, Any]], db: Session) -> None:
    """Migrate measurement data from JSON to PostgreSQL."""
    for measurement_data in measurements_data:
        # Create measurement
        measurement = Measurement(
            id=measurement_data.get('id', str(uuid.uuid4())),
            template_id=measurement_data.get('template_id', ''),
            measured_at=datetime.fromisoformat(measurement_data.get('measured_at')) if isinstance(measurement_data.get('measured_at'), str) else measurement_data.get('measured_at', datetime.utcnow()),
            recorded_at=datetime.fromisoformat(measurement_data.get('recorded_at')) if isinstance(measurement_data.get('recorded_at'), str) else measurement_data.get('recorded_at', datetime.utcnow()),
            notes=measurement_data.get('notes'),
            user_id=measurement_data.get('user_id', '')
        )
        
        db.add(measurement)
        db.flush()  # Get the ID
        
        # Create measurement values
        for value_data in measurement_data.get('values', []):
            # Find value definition
            value_def = db.query(ValueDefinition).filter(
                ValueDefinition.name == value_data.get('definition_name'),
                ValueDefinition.template_id == measurement.template_id
            ).first()
            
            if value_def:
                # Create measurement value
                value = MeasurementValue(
                    definition_id=value_def.id,
                    measurement_id=measurement.id,
                    value=value_data.get('value', 0.0)
                )
                
                db.add(value)
    
    db.commit()

def migrate_data(data_dir: str = "./data") -> None:
    """Migrate all data from JSON files to PostgreSQL."""
    # Make sure the database tables exist
    Base.metadata.create_all(engine)
    
    templates_file = os.path.join(data_dir, "templates.json")
    measurements_file = os.path.join(data_dir, "measurements.json")
    
    templates_data = load_json_file(templates_file)
    measurements_data = load_json_file(measurements_file)
    
    # Start a database session
    db = SessionLocal()
    
    try:
        # Migrate templates first (they are referenced by measurements)
        migrate_templates(templates_data, db)
        
        # Then migrate measurements
        migrate_measurements(measurements_data, db)
        
        print(f"Migration completed successfully.")
        print(f"Migrated {len(templates_data)} templates and {len(measurements_data)} measurements.")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate_data()