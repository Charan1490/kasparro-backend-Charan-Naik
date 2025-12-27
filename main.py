"""Main application entry point for deployment."""
import os
import uvicorn
from api.main import app

if __name__ == "__main__":
    # Get port from environment (Render sets this)
    port = int(os.getenv("PORT", 8000))
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
