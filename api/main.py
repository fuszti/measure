from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session

from models.measurement import Measurement, MeasurementTemplate, MeasurementValue
from db.storage import get_storage, Database
from db.database import get_db, engine, Base
from api.auth import (
    Token, User, authenticate_user, create_access_token, 
    get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(title="Life Measurements Tracker")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables on startup
@app.on_event("startup")
async def startup():
    # Create tables
    Base.metadata.create_all(bind=engine)

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/")
async def root():
    return {"message": "Welcome to the Life Measurements Tracker API"}

# Template endpoints
@app.get("/templates", response_model=List[MeasurementTemplate])
async def get_templates(
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_storage)
):
    return db.get_templates()

@app.get("/templates/{template_id}", response_model=MeasurementTemplate)
async def get_template(
    template_id: str, 
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_storage)
):
    template = db.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.post("/templates", response_model=MeasurementTemplate)
async def create_template(
    template: MeasurementTemplate, 
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_storage)
):
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
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_storage)
):
    if end_date is None:
        end_date = datetime.now()
    if start_date is None:
        start_date = end_date - timedelta(days=365)  # Default to last year
        
    return db.get_measurements(template_id, start_date, end_date)

@app.post("/measurements", response_model=Measurement)
async def create_measurement(
    measurement: Measurement, 
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_storage)
):
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
async def get_measurement(
    measurement_id: str, 
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_storage)
):
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
    current_user: User = Depends(get_current_active_user),
    db: Database = Depends(get_storage)
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