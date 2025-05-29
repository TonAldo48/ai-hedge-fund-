#!/usr/bin/env python3
"""
Standalone script to run the FastAPI backend server.
This allows the API to be run independently of the CLI application.
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Run the FastAPI application
    uvicorn.run(
        "app.backend.main:app",
        host=host,
        port=port,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    ) 