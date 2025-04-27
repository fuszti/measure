from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import List

from db.database import Base

class Unit(Base):
    __tablename__ = "units"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)  # e.g., "kg", "mmHg", "bpm"
    display_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    
    # Relationships
    value_definitions = relationship("ValueDefinition", back_populates="unit")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())


class ValueDefinition(Base):
    __tablename__ = "value_definitions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)  # e.g., "weight", "systolic", "diastolic"
    display_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    unit_id = Column(String, ForeignKey("units.id"), nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    template_id = Column(String, ForeignKey("measurement_templates.id"), nullable=False)
    
    # Relationships
    unit = relationship("Unit", back_populates="value_definitions")
    template = relationship("MeasurementTemplate", back_populates="value_definitions")
    measurement_values = relationship("MeasurementValue", back_populates="definition")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())


class MeasurementTemplate(Base):
    __tablename__ = "measurement_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)  # e.g., "Weight", "Blood Pressure"
    description = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)
    owner_id = Column(String, nullable=True)  # For user-created templates
    
    # Relationships
    value_definitions = relationship("ValueDefinition", back_populates="template", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="template")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())


class MeasurementValue(Base):
    __tablename__ = "measurement_values"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    definition_id = Column(String, ForeignKey("value_definitions.id"), nullable=False)
    measurement_id = Column(String, ForeignKey("measurements.id"), nullable=False)
    value = Column(Float, nullable=False)
    
    # Relationships
    definition = relationship("ValueDefinition", back_populates="measurement_values")
    measurement = relationship("Measurement", back_populates="values")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())


class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(String, ForeignKey("measurement_templates.id"), nullable=False)
    measured_at = Column(DateTime, nullable=False)  # Real time when measurement was taken
    recorded_at = Column(DateTime, nullable=False, default=datetime.utcnow)  # Time when measurement was recorded
    notes = Column(String, nullable=True)
    user_id = Column(String, nullable=False)
    
    # Relationships
    template = relationship("MeasurementTemplate", back_populates="measurements")
    values = relationship("MeasurementValue", back_populates="measurement", cascade="all, delete-orphan")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid.uuid4())