from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Unit(BaseModel):
    name: str  # e.g., "kg", "mmHg", "bpm"
    display_name: str
    description: Optional[str] = None


class ValueDefinition(BaseModel):
    name: str  # e.g., "weight", "systolic", "diastolic", "heart_rate"
    display_name: str
    description: Optional[str] = None
    unit: Unit
    min_value: Optional[float] = None
    max_value: Optional[float] = None


class MeasurementTemplate(BaseModel):
    id: str
    name: str  # e.g., "Weight", "Blood Pressure"
    description: Optional[str] = None
    value_definitions: List[ValueDefinition]
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    owner_id: Optional[str] = None  # For user-created templates


class MeasurementValue(BaseModel):
    definition_name: str
    value: float


class Measurement(BaseModel):
    id: str
    template_id: str
    values: List[MeasurementValue]
    measured_at: datetime  # Real time when measurement was taken
    recorded_at: datetime  # Time when measurement was recorded in system
    notes: Optional[str] = None
    user_id: str