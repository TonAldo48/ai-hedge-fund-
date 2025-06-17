"""
FastAPI routes for natural language financial analysis chat
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.backend.middleware.auth import verify_api_key
from app.backend.services.chat_agent import process_financial_query

router = APIRouter(prefix="/chat")

class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[Dict[str, str]]] = None

class ChatResponse(BaseModel):
    query: str
    response: str
    success: bool
    timestamp: str
    intermediate_steps: Optional[List] = None
    error: Optional[str] = None

@router.post("/analyze", response_model=ChatResponse)
async def chat_financial_analysis(
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Natural language financial analysis using LangChain agent.
    
    **Authentication Required**: This endpoint requires a valid API key.
    
    Examples:
    - "How does Apple's valuation look from a Peter Lynch perspective?"
    - "Analyze Tesla's growth using Warren Buffett's approach"
    - "What would Peter Lynch think about Microsoft's fundamentals?"
    """
    try:
        # Process the query using our LangChain agent
        result = await process_financial_query(
            query=request.query,
            chat_history=request.chat_history
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing financial analysis query: {str(e)}"
        )

@router.get("/examples")
async def get_example_queries():
    """
    Get example queries that can be used with the chat analysis endpoint.
    """
    return {
        "examples": [
            {
                "query": "How does Tesla's valuation look from a Peter Lynch perspective?",
                "description": "Analyzes TSLA using Peter Lynch's valuation methodology, focusing on PEG ratio and growth metrics"
            },
            {
                "query": "What would Warren Buffett think about Apple's fundamentals?",
                "description": "Applies Warren Buffett's fundamental analysis approach to AAPL"
            },
            {
                "query": "Analyze Microsoft's growth potential using Peter Lynch's approach",
                "description": "Uses Peter Lynch's growth analysis methodology for MSFT"
            },
            {
                "query": "How does Amazon look from a value investing perspective?",
                "description": "Applies value investing principles (Buffett-style) to AMZN analysis"
            }
        ],
        "supported_investors": [
            {
                "name": "Peter Lynch",
                "style": "Growth investing",
                "focus": "PEG ratio, earnings growth, fundamental strength"
            },
            {
                "name": "Warren Buffett", 
                "style": "Value investing",
                "focus": "Quality metrics, competitive moats, consistent returns"
            }
        ],
        "supported_analysis_types": [
            "Valuation analysis",
            "Growth analysis", 
            "Fundamental analysis",
            "Investment style comparison"
        ]
    } 