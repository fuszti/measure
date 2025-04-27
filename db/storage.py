from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from fastapi import Depends

from db.database import get_db
from db.models import Unit, ValueDefinition, MeasurementTemplate, Measurement, MeasurementValue
from models.measurement import (
    Unit as UnitSchema,
    ValueDefinition as ValueDefinitionSchema,
    MeasurementTemplate as MeasurementTemplateSchema,
    Measurement as MeasurementSchema,
    MeasurementValue as MeasurementValueSchema,
)

class Database:
    def __init__(self, db: Session):
        self.db = db
    
    def get_templates(self) -> List[MeasurementTemplateSchema]:
        templates = self.db.query(MeasurementTemplate).filter(MeasurementTemplate.is_active == True).all()
        return [self._convert_template_to_schema(template) for template in templates]
    
    def get_template(self, template_id: str) -> Optional[MeasurementTemplateSchema]:
        template = self.db.query(MeasurementTemplate).filter(
            MeasurementTemplate.id == template_id,
            MeasurementTemplate.is_active == True
        ).first()
        
        if not template:
            return None
            
        return self._convert_template_to_schema(template)
    
    def create_template(self, template_schema: MeasurementTemplateSchema) -> MeasurementTemplateSchema:
        # Check if template with this ID already exists
        existing_template = self.db.query(MeasurementTemplate).filter(
            MeasurementTemplate.id == template_schema.id
        ).first()
        
        if existing_template:
            # Update existing template
            existing_template.name = template_schema.name
            existing_template.description = template_schema.description
            existing_template.updated_at = datetime.utcnow()
            existing_template.is_active = template_schema.is_active
            existing_template.owner_id = template_schema.owner_id
            
            # Remove existing value definitions
            for value_def in existing_template.value_definitions:
                self.db.delete(value_def)
            
            # Add new value definitions
            for value_def_schema in template_schema.value_definitions:
                # Create unit if it doesn't exist
                unit = self.db.query(Unit).filter(Unit.name == value_def_schema.unit.name).first()
                if not unit:
                    unit = Unit(
                        name=value_def_schema.unit.name,
                        display_name=value_def_schema.unit.display_name,
                        description=value_def_schema.unit.description
                    )
                    self.db.add(unit)
                    self.db.flush()
                
                # Create value definition
                value_def = ValueDefinition(
                    name=value_def_schema.name,
                    display_name=value_def_schema.display_name,
                    description=value_def_schema.description,
                    unit_id=unit.id,
                    min_value=value_def_schema.min_value,
                    max_value=value_def_schema.max_value,
                    template_id=existing_template.id
                )
                self.db.add(value_def)
            
            template = existing_template
        else:
            # Create new template
            template = MeasurementTemplate(
                id=template_schema.id,
                name=template_schema.name,
                description=template_schema.description,
                created_at=template_schema.created_at,
                updated_at=template_schema.updated_at,
                is_active=template_schema.is_active,
                owner_id=template_schema.owner_id
            )
            self.db.add(template)
            self.db.flush()
            
            # Add value definitions
            for value_def_schema in template_schema.value_definitions:
                # Create unit if it doesn't exist
                unit = self.db.query(Unit).filter(Unit.name == value_def_schema.unit.name).first()
                if not unit:
                    unit = Unit(
                        name=value_def_schema.unit.name,
                        display_name=value_def_schema.unit.display_name,
                        description=value_def_schema.unit.description
                    )
                    self.db.add(unit)
                    self.db.flush()
                
                # Create value definition
                value_def = ValueDefinition(
                    name=value_def_schema.name,
                    display_name=value_def_schema.display_name,
                    description=value_def_schema.description,
                    unit_id=unit.id,
                    min_value=value_def_schema.min_value,
                    max_value=value_def_schema.max_value,
                    template_id=template.id
                )
                self.db.add(value_def)
        
        self.db.commit()
        
        return self._convert_template_to_schema(template)
    
    def get_measurements(
        self, 
        template_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[MeasurementSchema]:
        query = self.db.query(Measurement)
        
        # Apply filters
        if template_id:
            query = query.filter(Measurement.template_id == template_id)
        
        if start_date:
            query = query.filter(Measurement.measured_at >= start_date)
            
        if end_date:
            query = query.filter(Measurement.measured_at <= end_date)
        
        # Order by measured_at descending (most recent first)
        query = query.order_by(desc(Measurement.measured_at))
        
        measurements = query.all()
        
        return [self._convert_measurement_to_schema(measurement) for measurement in measurements]
    
    def get_measurement(self, measurement_id: str) -> Optional[MeasurementSchema]:
        measurement = self.db.query(Measurement).filter(Measurement.id == measurement_id).first()
        
        if not measurement:
            return None
            
        return self._convert_measurement_to_schema(measurement)
    
    def create_measurement(self, measurement_schema: MeasurementSchema) -> MeasurementSchema:
        # Check if measurement with this ID already exists
        existing_measurement = self.db.query(Measurement).filter(
            Measurement.id == measurement_schema.id
        ).first()
        
        if existing_measurement:
            # Update existing measurement
            existing_measurement.template_id = measurement_schema.template_id
            existing_measurement.measured_at = measurement_schema.measured_at
            existing_measurement.notes = measurement_schema.notes
            existing_measurement.user_id = measurement_schema.user_id
            
            # Remove existing values
            for value in existing_measurement.values:
                self.db.delete(value)
            
            # Add new values
            for value_schema in measurement_schema.values:
                # Find value definition
                value_def = self.db.query(ValueDefinition).join(
                    MeasurementTemplate
                ).filter(
                    ValueDefinition.name == value_schema.definition_name,
                    MeasurementTemplate.id == measurement_schema.template_id
                ).first()
                
                if not value_def:
                    raise ValueError(f"Value definition '{value_schema.definition_name}' not found for template '{measurement_schema.template_id}'")
                
                # Create measurement value
                value = MeasurementValue(
                    definition_id=value_def.id,
                    measurement_id=existing_measurement.id,
                    value=value_schema.value
                )
                self.db.add(value)
            
            measurement = existing_measurement
        else:
            # Create new measurement
            measurement = Measurement(
                id=measurement_schema.id,
                template_id=measurement_schema.template_id,
                measured_at=measurement_schema.measured_at,
                recorded_at=measurement_schema.recorded_at,
                notes=measurement_schema.notes,
                user_id=measurement_schema.user_id
            )
            self.db.add(measurement)
            self.db.flush()
            
            # Add values
            for value_schema in measurement_schema.values:
                # Find value definition
                value_def = self.db.query(ValueDefinition).join(
                    MeasurementTemplate
                ).filter(
                    ValueDefinition.name == value_schema.definition_name,
                    MeasurementTemplate.id == measurement_schema.template_id
                ).first()
                
                if not value_def:
                    raise ValueError(f"Value definition '{value_schema.definition_name}' not found for template '{measurement_schema.template_id}'")
                
                # Create measurement value
                value = MeasurementValue(
                    definition_id=value_def.id,
                    measurement_id=measurement.id,
                    value=value_schema.value
                )
                self.db.add(value)
        
        self.db.commit()
        
        return self._convert_measurement_to_schema(measurement)
    
    def _convert_template_to_schema(self, template: MeasurementTemplate) -> MeasurementTemplateSchema:
        value_definitions = []
        
        for value_def in template.value_definitions:
            unit_schema = UnitSchema(
                name=value_def.unit.name,
                display_name=value_def.unit.display_name,
                description=value_def.unit.description
            )
            
            value_def_schema = ValueDefinitionSchema(
                name=value_def.name,
                display_name=value_def.display_name,
                description=value_def.description,
                unit=unit_schema,
                min_value=value_def.min_value,
                max_value=value_def.max_value
            )
            
            value_definitions.append(value_def_schema)
        
        return MeasurementTemplateSchema(
            id=template.id,
            name=template.name,
            description=template.description,
            value_definitions=value_definitions,
            created_at=template.created_at,
            updated_at=template.updated_at,
            is_active=template.is_active,
            owner_id=template.owner_id
        )
    
    def _convert_measurement_to_schema(self, measurement: Measurement) -> MeasurementSchema:
        values = []
        
        for value in measurement.values:
            value_schema = MeasurementValueSchema(
                definition_name=value.definition.name,
                value=value.value
            )
            
            values.append(value_schema)
        
        return MeasurementSchema(
            id=measurement.id,
            template_id=measurement.template_id,
            values=values,
            measured_at=measurement.measured_at,
            recorded_at=measurement.recorded_at,
            notes=measurement.notes,
            user_id=measurement.user_id
        )


# Dependency for FastAPI
def get_storage(db: Session = Depends(get_db)):
    return Database(db)