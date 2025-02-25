from typing import List, Optional, Dict
from datetime import datetime
import json
import os
from models.measurement import Measurement, MeasurementTemplate

class Database:
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        self.templates_file = os.path.join(data_dir, "templates.json")
        self.measurements_file = os.path.join(data_dir, "measurements.json")
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        if not os.path.exists(self.templates_file):
            with open(self.templates_file, "w") as f:
                json.dump([], f)
                
        if not os.path.exists(self.measurements_file):
            with open(self.measurements_file, "w") as f:
                json.dump([], f)
    
    def get_templates(self) -> List[MeasurementTemplate]:
        with open(self.templates_file, "r") as f:
            data = json.load(f)
            return [MeasurementTemplate(**template) for template in data]
    
    def get_template(self, template_id: str) -> Optional[MeasurementTemplate]:
        templates = self.get_templates()
        for template in templates:
            if template.id == template_id:
                return template
        return None
    
    def create_template(self, template: MeasurementTemplate) -> MeasurementTemplate:
        templates = self.get_templates()
        
        # Check if template with this ID already exists, update if so
        for i, existing in enumerate(templates):
            if existing.id == template.id:
                templates[i] = template
                break
        else:
            # Template doesn't exist, add it
            templates.append(template)
        
        # Save to file
        with open(self.templates_file, "w") as f:
            json.dump([t.dict() for t in templates], f, default=self._json_serializer)
            
        return template
    
    def get_measurements(
        self, 
        template_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Measurement]:
        with open(self.measurements_file, "r") as f:
            data = json.load(f)
            measurements = [Measurement(**m) for m in data]
        
        # Apply filters
        if template_id:
            measurements = [m for m in measurements if m.template_id == template_id]
        
        if start_date:
            measurements = [
                m for m in measurements 
                if (isinstance(m.measured_at, str) and datetime.fromisoformat(m.measured_at) >= start_date) or
                (isinstance(m.measured_at, datetime) and m.measured_at >= start_date)
            ]
            
        if end_date:
            measurements = [
                m for m in measurements 
                if (isinstance(m.measured_at, str) and datetime.fromisoformat(m.measured_at) <= end_date) or
                (isinstance(m.measured_at, datetime) and m.measured_at <= end_date)
            ]
            
        return measurements
    
    def get_measurement(self, measurement_id: str) -> Optional[Measurement]:
        measurements = self.get_measurements()
        for measurement in measurements:
            if measurement.id == measurement_id:
                return measurement
        return None
    
    def create_measurement(self, measurement: Measurement) -> Measurement:
        measurements = self.get_measurements()
        
        # Check if measurement with this ID already exists, update if so
        for i, existing in enumerate(measurements):
            if existing.id == measurement.id:
                measurements[i] = measurement
                break
        else:
            # Measurement doesn't exist, add it
            measurements.append(measurement)
        
        # Save to file
        with open(self.measurements_file, "w") as f:
            json.dump([m.dict() for m in measurements], f, default=self._json_serializer)
            
        return measurement
    
    def _json_serializer(self, obj):
        """Helper method to serialize datetime objects."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")


# Dependency for FastAPI
def get_db():
    return Database()