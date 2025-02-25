import uvicorn
import os
import webbrowser
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

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

if __name__ == "__main__":
    print("Starting Life Measurements Tracker...")
    
    # Start the frontend server in a separate thread
    frontend_thread = threading.Thread(target=start_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    # Start the backend server
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)