from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.backend.routes import api_router

# Create FastAPI app with metadata
app = FastAPI(
    title="AI Hedge Fund API",
    description="""
    ## AI-Powered Hedge Fund Trading API
    
    This API provides endpoints to run AI-powered trading analysis using multiple AI agents.
    
    ### Features:
    - Multiple AI analyst agents (technical, fundamental, sentiment, etc.)
    - Support for various LLM models (OpenAI, Anthropic, etc.)
    - Real-time streaming updates via Server-Sent Events
    - Synchronous endpoint for simple testing
    
    ### Getting Started:
    1. Get available agents: `GET /hedge-fund/agents`
    2. Get available models: `GET /hedge-fund/models`
    3. Run analysis: `POST /hedge-fund/run-sync` (for testing) or `POST /hedge-fund/run` (for streaming)
    """,
    version="0.1.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(api_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Hedge Fund API",
        "documentation": "/docs",
        "health_check": "/health"
    }
