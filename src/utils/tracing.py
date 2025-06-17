import os
from typing import Optional, Dict, Any
from datetime import datetime
from langsmith import Client, traceable
from langchain.globals import set_verbose


def setup_langsmith_tracing(
    project_name: Optional[str] = None,
    environment: str = "production"
) -> Client:
    """Setup LangSmith tracing for the hedge fund system."""
    
    # Check if LangSmith is properly configured
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key:
        print("Warning: LANGCHAIN_API_KEY not found. LangSmith tracing will be disabled.")
        print("To enable tracing, add LANGCHAIN_API_KEY to your .env file.")
        return None
    
    # Set project name based on environment
    if not project_name:
        env_project_map = {
            "development": "ai-hedge-fund-dev",
            "staging": "ai-hedge-fund-staging", 
            "production": "ai-hedge-fund-production"
        }
        project_name = env_project_map.get(environment, "ai-hedge-fund")
    
    # Set environment variables for LangChain tracing
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = project_name
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    
    # Enable verbose logging for debugging in development
    if environment == "development":
        set_verbose(True)
    
    try:
        # Initialize LangSmith client
        client = Client()
        print(f"✅ LangSmith tracing enabled for project: {project_name}")
        return client
    except Exception as e:
        print(f"❌ Failed to initialize LangSmith client: {e}")
        return None


def create_agent_session_metadata(
    session_id: str,
    agent_name: str,
    tickers: list,
    model_name: str,
    model_provider: str,
    metadata: dict = None
) -> dict:
    """Create standardized metadata for hedge fund agent sessions."""
    
    session_metadata = {
        "session_id": session_id,
        "agent_name": agent_name,
        "agent_type": "hedge_fund_analyst",
        "tickers": tickers,
        "model_name": model_name,
        "model_provider": model_provider,
        "timestamp": datetime.now().isoformat(),
        "system": "ai-hedge-fund",
        **(metadata or {})
    }
    
    return session_metadata


def get_tracing_enabled() -> bool:
    """Check if LangSmith tracing is properly configured and enabled."""
    return (
        os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true" and
        os.getenv("LANGCHAIN_API_KEY") is not None
    )


# Removed log_agent_analysis function to prevent incomplete traces
# All tracing is now handled automatically by @traceable decorators 