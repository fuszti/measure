# Life Measurements Tracker - Development Guide

## Commands
- Run API server: `uvicorn api.main:app --reload`
- Run frontend: `cd web && python -m http.server 8080`
- Run full app: `python run.py`
- Install dependencies: `pip install -r requirements.txt`

## Style Guidelines
- **Imports**: Group by standard lib, third-party, local imports with line breaks between groups
- **Typing**: Use typing hints for all function parameters and return values
- **Naming**: snake_case for variables/functions, PascalCase for classes, ALL_CAPS for constants
- **Models**: Use Pydantic BaseModel for data validation
- **Error Handling**: Use FastAPI's HTTPException with appropriate status codes
- **API Endpoints**: Use async functions with clear input/output models
- **JSON Handling**: Use proper serialization for datetime objects
- **Frontend**: Follow modern JavaScript practices with clean DOM manipulation
- **Constants**: Define configuration values at the top of files
- **Comments**: Document complex logic and business rules