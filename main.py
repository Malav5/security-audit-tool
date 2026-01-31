import sys
import os

# Add the 'backend' folder to the system path so imports work correctly
sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

# Import the FastAPI app from the backend directory
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
