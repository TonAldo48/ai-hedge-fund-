from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import api_router

# Create FastAPI app with metadata
app = FastAPI(
    title="AI Hedge Fund API",
    description="""
    ## AI-Powered Hedge Fund Trading API
    
    This API provides endpoints to run AI-powered trading analysis using multiple AI agents.
    
    ### 🔐 Authentication
    
    **Production**: API key required for all protected endpoints.
    
    **Authentication Methods:**
    1. **Header**: `X-API-Key: your-api-key`
    2. **Bearer Token**: `Authorization: Bearer your-api-key`
    
    **Development**: If no `API_KEY` or `HEDGE_FUND_API_KEY` environment variable is set, authentication is disabled.
    
    ### 🚀 Features:
    - Multiple AI analyst agents (Warren Buffett, Peter Lynch, Technical Analyst, etc.)
    - Support for various LLM models (OpenAI, Anthropic, DeepSeek, etc.)
    - Real-time streaming updates via Server-Sent Events
    - Synchronous endpoint for simple testing
    - Production-ready authentication
    
    ### 📚 Getting Started:
    1. **Public endpoints** (no auth required):
       - `GET /` - API information
       - `GET /health` - Health check
       - `GET /hedge-fund/agents` - List available agents
       - `GET /hedge-fund/models` - List available models
    
    2. **Protected endpoints** (API key required):
       - `POST /hedge-fund/run-sync` - Synchronous analysis
       - `POST /hedge-fund/run` - Streaming analysis
    
    ### 💡 Example Usage:
    ```bash
    # With X-API-Key header
    curl -H "X-API-Key: your-api-key" -X POST "/hedge-fund/run-sync" ...
    
    # With Bearer token
    curl -H "Authorization: Bearer your-api-key" -X POST "/hedge-fund/run-sync" ...
    ```
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

# Root endpoint (public - no authentication required)
@app.get("/")
async def root():
    return {
        "message": "Welcome to AI Hedge Fund API",
        "version": "0.1.0",
        "documentation": "/docs",
        "health_check": "/health",
        "authentication": {
            "required_for": ["/hedge-fund/run-sync", "/hedge-fund/run"],
            "methods": ["X-API-Key header", "Bearer token"],
            "development_mode": "Authentication disabled if no API_KEY environment variable"
        },
        "public_endpoints": [
            "/",
            "/health", 
            "/hedge-fund/agents",
            "/hedge-fund/models"
        ]
    }
