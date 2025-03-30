"""
Entry point for the Legal Sanctions RAG application.
"""

import os
import sys
import logging
import dotenv
from pathlib import Path

# Add the project root directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Optionally, if needed, also add the app directory:
sys.path.insert(0, str(Path(__file__).resolve().parent / "app"))

# Load environment variables
dotenv.load_dotenv()

# Set OpenMP environment variable to fix thread warning
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["OMP_NUM_THREADS"] = "1"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

from app.main import app

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Check if debug mode is enabled
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    if debug:
        # Run in debug mode with Flask's development server
        app.run(host=host, port=port, debug=True)
    else:
        try:
            # Try to import waitress for production server
            from waitress import serve
            logging.info(f"Starting production server on http://{host}:{port}")
            serve(app, host=host, port=port, threads=8)
        except ImportError:
            # Fall back to Flask's built-in server
            logging.warning("Waitress not installed. Using Flask's development server.")
            logging.warning("This is not recommended for production use.")
            app.run(host=host, port=port, debug=False)