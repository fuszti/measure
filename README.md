# Life Measurements Tracker

A flexible web application for tracking, visualizing, and analyzing personal measurements over time. Uses PostgreSQL database for scalable and reliable storage.

## Features

- Create custom measurement templates with multiple values and units
- Track measurements with timestamps (recorded and measured times)
- Visualize measurements on interactive charts
- View statistics for different time periods
- Extensible design allowing for user-created measurement templates
- PostgreSQL database for robust and scalable storage
- Docker Compose for easy deployment and development

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
- Docker and Docker Compose (recommended)
- PostgreSQL (if not using Docker)
- Cloudflare account (for Cloudflare Tunnel deployment)

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```
   
### Authentication

The application uses JWT-based authentication with username/password credentials. Default login is:

- Username: `admin`
- Password: `password`

To customize user credentials, set the `AUTH_USERS` environment variable in the format:
```
AUTH_USERS=username1:password1,username2:password2
```

For production, you should also set a custom `SECRET_KEY` environment variable:
```
SECRET_KEY=your-secure-random-key
```

### Running the Application

#### Using Docker Compose (Recommended)

1. Start the application stack:
   ```
   python run.py
   ```
   Or directly with Docker Compose:
   ```
   docker-compose up -d
   ```

2. Navigate to http://localhost:8080 in your browser

#### Standalone Mode

1. Make sure PostgreSQL is running and accessible with the connection details in `.env`

2. Start the application in standalone mode:
   ```
   python run.py --standalone
   ```

3. Or start components separately:
   ```
   # Start the backend API
   uvicorn api.main:app --reload
   
   # Open the web interface
   cd web
   python -m http.server 8080
   ```

4. Navigate to http://localhost:8080 in your browser

### Database Migration

If you're upgrading from the JSON file storage:

1. Start PostgreSQL (via Docker Compose or locally)
2. Run the migration script:
   ```
   python -m db.migrate_data
   ```

### Testing

The project includes comprehensive automated tests for the database, API, and Docker setup.

#### Running Tests

You can run the tests using the provided script:

```bash
# Run all tests
./run_tests.py

# Run tests with coverage report
./run_tests.py --coverage

# Skip Docker-based tests
./run_tests.py --skip-docker

# Run only unit tests
./run_tests.py --unit-only
```

Alternatively, you can use pytest directly:

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=measure --cov=api --cov=db --cov=models

# Run specific test file
pytest tests/test_api.py
```

## Architecture

- **Backend**: FastAPI-based RESTful API
- **Frontend**: Vanilla JavaScript with Bootstrap UI
- **Storage**: PostgreSQL database with SQLAlchemy ORM
- **Models**: Pydantic models for API validation, SQLAlchemy models for database
- **Migration**: Alembic for database schema migrations
- **Authentication**: JWT-based authentication with username/password
- **Deployment**: Docker Compose with NGINX and Cloudflare Tunnel

## Deploying with Cloudflare Tunnel

To deploy the application securely on the internet using Cloudflare Tunnel:

1. Sign up for a Cloudflare account and install `cloudflared` on your server

2. Authenticate with Cloudflare:
   ```
   cloudflared tunnel login
   ```

3. Create a tunnel:
   ```
   cloudflared tunnel create measure-app
   ```

4. Configure the tunnel in `~/.cloudflared/config.yml`:
   ```yml
   tunnel: <TUNNEL_ID>
   credentials-file: /root/.cloudflared/<TUNNEL_ID>.json

   ingress:
     - hostname: measure.yourdomain.com
       service: http://localhost:8080
     - service: http_status:404
   ```

5. Start your application with Docker Compose:
   ```
   docker-compose up -d
   ```

6. Start the Cloudflare Tunnel:
   ```
   cloudflared tunnel run measure-app
   ```

7. Configure your DNS to point to the tunnel:
   ```
   cloudflared tunnel route dns measure-app measure.yourdomain.com
   ```

## Project Structure

```
measure/
├── api/           # Backend API endpoints
├── db/            # Database models and connections
│   ├── database.py     # Database connection setup
│   ├── models.py       # SQLAlchemy ORM models
│   ├── storage.py      # Database access layer
│   └── migrate_data.py # JSON to PostgreSQL migration
├── migrations/    # Alembic database migrations
├── models/        # API data models (Pydantic)
├── web/           # Frontend web interface
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── data/          # JSON data files (legacy)
├── docker-compose.yml  # Docker services definition
├── Dockerfile          # API service container definition
└── .env                # Environment configuration
```

## License

MIT