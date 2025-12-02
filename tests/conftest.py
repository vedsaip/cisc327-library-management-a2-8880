
import pytest
from threading import Thread
import time
import requests
from app import create_app
from database import init_database, clear_database
from routes.shutdown_routes import shutdown_bp
import os
import sys

# Add project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_app(flask_app):
    # Running in debug mode is not recommended for production but fine for tests
    flask_app.run(port=5000, debug=False, use_reloader=False)

@pytest.fixture(scope="function")
def app():
    """Session-wide test Flask application."""
    # Initialize and clear the database before each test
    init_database()
    clear_database()
    
    flask_app = create_app()
    flask_app.register_blueprint(shutdown_bp)

    
    app_thread = Thread(target=run_app, args=(flask_app,))
    app_thread.daemon = True
    app_thread.start()
    
    # Wait for the app to start
    retries = 5
    while retries > 0:
        try:
            response = requests.get("http://localhost:5000")
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(0.5)
        retries -= 1
    
    yield flask_app

    # Shutdown the server
    requests.post("http://localhost:5000/shutdown")
    app_thread.join()
