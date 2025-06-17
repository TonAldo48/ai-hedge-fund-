from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path

# Add parent directory to path so we can import from 'src'
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

from app.backend.routes import api_router

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
    - Multiple AI analyst agents (Warren Buffett, Peter Lynch, Charlie Munger, Ben Graham, Technical Analyst, etc.)
    - Natural language chat interface for each agent
    - Support for various LLM models (OpenAI, Anthropic, DeepSeek, etc.)
    - Real-time streaming updates via Server-Sent Events
    - Multi-agent comparison and consensus building
    - Production-ready authentication
    
    ### 📚 Getting Started:
    1. **Public endpoints** (no auth required):
       - `GET /` - API information
       - `GET /health` - Health check
       - `GET /hedge-fund/agents` - List available agents
       - `GET /hedge-fund/models` - List available models
    
    2. **Protected endpoints** (API key required):
       - `POST /hedge-fund/run-sync` - Synchronous hedge fund analysis
       - `POST /hedge-fund/run` - Streaming hedge fund analysis
       - `GET /api/agents/` - List all chat agents with capabilities
       - `POST /api/agents/{agent_name}/analyze` - Chat with specific agent
       - `POST /api/agents/{agent_name}/analyze-streaming` - Stream agent responses
       - `POST /api/agents/compare` - Compare multiple agent perspectives
       - `GET /api/agents/recommend` - Get agent recommendation for query
    
    ### 💡 Example Usage:
    ```bash
    # List available chat agents
    curl -H "X-API-Key: your-api-key" "/api/agents/"
    
    # Chat with Warren Buffett
    curl -H "Authorization: Bearer your-api-key" -X POST "/api/agents/warren_buffett/analyze" \\
      -d '{"query": "What do you think about Apple's moat?"}'
    
    # Compare multiple perspectives
    curl -H "X-API-Key: your-api-key" -X POST "/api/agents/compare" \\
      -d '{"query": "Should I buy Tesla?", "selected_agents": ["warren_buffett", "peter_lynch", "technical_analyst"]}'
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
            "required_for": ["/hedge-fund/run-sync", "/hedge-fund/run", "/api/agents/*"],
            "methods": ["X-API-Key header", "Bearer token"],
            "development_mode": "Authentication disabled if no API_KEY environment variable"
        },
        "public_endpoints": [
            "/",
            "/health", 
            "/hedge-fund/agents",
            "/hedge-fund/models"
        ],
        "chat_agents": [
            "warren_buffett",
            "peter_lynch", 
            "charlie_munger",
            "ben_graham",
            "technical_analyst"
        ]
    }
