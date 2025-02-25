# Life Measurements Tracker

A flexible web application for tracking, visualizing, and analyzing personal measurements over time.

## Features

- Create custom measurement templates with multiple values and units
- Track measurements with timestamps (recorded and measured times)
- Visualize measurements on interactive charts
- View statistics for different time periods
- Extensible design allowing for user-created measurement templates

## Examples

- Weight tracking (single measurement with kg/lbs units)
- Blood pressure tracking (multiple measurements: systolic, diastolic, heart rate)
- Workout tracking (reps, sets, weight)
- Glucose levels
- Sleep metrics
- And many more!

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js (for development)

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the backend API:
   ```
   uvicorn api.main:app --reload
   ```

2. Open the web interface:
   ```
   cd web
   python -m http.server 8080
   ```

3. Navigate to http://localhost:8080 in your browser

## Architecture

- **Backend**: FastAPI-based RESTful API
- **Frontend**: Vanilla JavaScript with Bootstrap UI
- **Storage**: JSON file-based storage (can be extended to databases)
- **Models**: Pydantic models for data validation

## Project Structure

```
measure/
├── api/           # Backend API endpoints
├── db/            # Data storage layer
├── models/        # Data models
├── web/           # Frontend web interface
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── data/          # Data storage (created at runtime)
```

## License

MIT