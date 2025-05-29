#!/usr/bin/env python3
"""
Standalone script to run the FastAPI backend server.
This allows the API to be run independently of the CLI application.
"""
import uvicorn
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path so we can import from 'src'
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get configuration from environment
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    environment = os.getenv("ENVIRONMENT", "development")
    
    # Disable auto-reload in production
    reload = environment.lower() == "development"
    
    print(f"🚀 Starting AI Hedge Fund API server...")
    print(f"   Environment: {environment}")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Auto-reload: {reload}")
    print(f"   Health check: http://{host}:{port}/health")
    print(f"   API docs: http://{host}:{port}/docs")
    
    # Run the FastAPI application
    # Use relative import when running from app/ directory
    uvicorn.run(
        "backend.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 