import uvicorn
import os
import webbrowser
import threading
import time
import subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://measure:measure123@localhost:5432/measure")

def start_frontend():
    # Wait a bit for the backend to start
    time.sleep(2)
    
    # Change to the web directory
    os.chdir("web")
    
    # Create a simple HTTP server for the frontend
    httpd = HTTPServer(("localhost", 8080), SimpleHTTPRequestHandler)
    print("Frontend server started at http://localhost:8080")
    
    # Open the browser
    webbrowser.open("http://localhost:8080")
    
    # Start serving
    httpd.serve_forever()

def start_docker_compose():
    """Start the application using Docker Compose."""
    try:
        print("Starting with Docker Compose...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        print("Docker Compose started successfully.")
        print("API available at: http://localhost:8000")
        print("Web interface available at: http://localhost:8080")
        
        # Open the browser
        webbrowser.open("http://localhost:8080")
    except subprocess.CalledProcessError as e:
        print(f"Error starting Docker Compose: {e}")
    except FileNotFoundError:
        print("Docker Compose not found. Please install Docker Compose to use this feature.")
        print("Falling back to standalone mode...")
        start_standalone()

def start_standalone():
    """Start the application in standalone mode."""
    print("Starting in standalone mode...")
    
    # Start the frontend server in a separate thread
    frontend_thread = threading.Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # Start the backend server
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    print("Starting Life Measurements Tracker...")
    
    # Check if --standalone flag is provided
    import sys
    if "--standalone" in sys.argv:
        start_standalone()
    else:
        # Try to use Docker Compose by default
        start_docker_compose()