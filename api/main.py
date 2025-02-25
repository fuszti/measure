from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from models.measurement import Measurement, MeasurementTemplate, MeasurementValue
from db.storage import get_db, Database

app = FastAPI(title="Life Measurements Tracker")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Life Measurements Tracker API"}

# Template endpoints
@app.get("/templates", response_model=List[MeasurementTemplate])
async def get_templates(db: Database = Depends(get_db)):
    return db.get_templates()

@app.get("/templates/{template_id}", response_model=MeasurementTemplate)
async def get_template(template_id: str, db: Database = Depends(get_db)):
    template = db.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.post("/templates", response_model=MeasurementTemplate)
async def create_template(template: MeasurementTemplate, db: Database = Depends(get_db)):
    if not template.id:
        template.id = str(uuid.uuid4())
    template.created_at = datetime.now()
    return db.create_template(template)

# Measurement endpoints
@app.get("/measurements", response_model=List[Measurement])
async def get_measurements(
    template_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Database = Depends(get_db)
):
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=30)  # Default to last 30 days
        
    return db.get_measurements(template_id, start_date, end_date)

@app.post("/measurements", response_model=Measurement)
async def create_measurement(measurement: Measurement, db: Database = Depends(get_db)):
    if not measurement.id:
        measurement.id = str(uuid.uuid4())
    if not measurement.recorded_at:
        measurement.recorded_at = datetime.now()
        
    # Validate against template
    template = db.get_template(measurement.template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Validate all required values are present
    template_value_names = {vd.name for vd in template.value_definitions}
    measurement_value_names = {v.definition_name for v in measurement.values}
    
    if not template_value_names.issubset(measurement_value_names):
        missing = template_value_names - measurement_value_names
        raise HTTPException(status_code=400, detail=f"Missing required values: {missing}")
    
    return db.create_measurement(measurement)

@app.get("/measurements/{measurement_id}", response_model=Measurement)
async def get_measurement(measurement_id: str, db: Database = Depends(get_db)):
    measurement = db.get_measurement(measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement

# Statistics endpoints
@app.get("/statistics/{template_id}")
async def get_statistics(
    template_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Database = Depends(get_db)
):
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=30)  # Default to last 30 days
    
    template = db.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    measurements = db.get_measurements(template_id, start_date, end_date)
    
    # Calculate statistics for each value definition
    stats = {}
    for value_def in template.value_definitions:
        values = [
            m.values[i].value 
            for m in measurements
            for i, v in enumerate(m.values) 
            if v.definition_name == value_def.name
        ]
        
        if values:
            stats[value_def.name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "unit": value_def.unit.name
            }
        else:
            stats[value_def.name] = {
                "count": 0,
                "unit": value_def.unit.name
            }
    
    return stats