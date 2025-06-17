"""
Warren Buffett Chat API Routes
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import json
import asyncio

from app.backend.services.warren_buffett_chat_agent import process_warren_buffett_query
from app.backend.middleware.auth import verify_api_key
from app.backend.models import ErrorResponse, ChatMessage, ChatResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/warren-buffett", tags=["warren-buffett-chat"])

class StreamingChatMessage(BaseModel):
    query: str
    chat_history: List[ChatMessage] = []

@router.post("/analyze")
async def analyze_warren_buffett(
    query: str = Query(..., description="Natural language financial analysis query"),
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze stocks using Warren Buffett's investment philosophy.
    """
    try:
        result = await process_warren_buffett_query(query)
        return ChatResponse(
            response=result["response"],
            success=result["success"],
            timestamp=result["timestamp"],
            agent="warren_buffett"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-streaming")
async def analyze_warren_buffett_streaming(
    request: StreamingChatMessage,
    api_key: str = Depends(verify_api_key)
):
    """
    Stream Warren Buffett's analysis process in real-time using Server-Sent Events.
    
    Returns a stream of events showing:
    - Agent thinking process
    - Tool usage and data fetching
    - Analysis steps and decisions
    - Final response
    """
    try:
        from app.backend.services.warren_buffett_chat_agent import get_warren_buffett_agent
        
        async def ask_agent():
            agent = get_warren_buffett_agent()
            
            chat_history = []
            for msg in request.chat_history:
                chat_history.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Get the generator from the agent
            response_generator = agent.analyze_streaming_v2(request.query, chat_history)

            # Stream the response
            async for chunk in response_generator:
                yield chunk

        return StreamingResponse(ask_agent(), media_type="text/event-stream")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start streaming analysis: {str(e)}")

@router.get("/capabilities")
async def get_warren_buffett_capabilities():
    """Get information about Warren Buffett agent's analysis capabilities."""
    return {
        "agent": "Warren Buffett",
        "description": "Value investing analysis using Warren Buffett's legendary principles",
        "capabilities": [
            {
                "name": "Fundamentals Analysis",
                "description": "Evaluates ROE, debt levels, operating margins, and liquidity position",
                "example": "How strong are Apple's fundamentals?"
            },
            {
                "name": "Competitive Moat Analysis", 
                "description": "Assesses durable competitive advantages through stable ROE and margins",
                "example": "Does Coca-Cola have a strong moat?"
            },
            {
                "name": "Earnings Consistency Analysis",
                "description": "Analyzes earnings stability and growth trends over multiple periods", 
                "example": "How consistent are Microsoft's earnings?"
            },
            {
                "name": "Management Quality Analysis",
                "description": "Evaluates share buybacks, dividends, and capital allocation decisions",
                "example": "How well does Apple's management allocate capital?"
            },
            {
                "name": "Intrinsic Value Analysis",
                "description": "Calculates DCF valuation with margin of safety using owner earnings",
                "example": "What's Tesla's intrinsic value?"
            },
            {
                "name": "Owner Earnings Analysis", 
                "description": "Calculates true cash-generating ability (Net Income + Depreciation - Maintenance CapEx)",
                "example": "What are Amazon's owner earnings?"
            }
        ],
        "investment_philosophy": [
            "Circle of Competence: Only invest in businesses you understand",
            "Margin of Safety (>30%): Buy at significant discount to intrinsic value",
            "Economic Moat: Look for durable competitive advantages", 
            "Quality Management: Seek conservative, shareholder-oriented teams",
            "Financial Strength: Favor low debt, strong returns on equity",
            "Long-term Horizon: Invest in businesses, not just stocks",
            "Owner Earnings: Focus on true cash-generating ability"
        ],
        "example_queries": [
            "What do you think about Apple's competitive moat?",
            "How does Microsoft's management allocate capital?", 
            "What's Tesla's intrinsic value and margin of safety?",
            "Should I invest in Berkshire Hathaway Class B?",
            "How strong are Amazon's fundamentals?",
            "Does Coca-Cola still have pricing power?",
            "What are your thoughts on investing in tech stocks?",
            "How do you evaluate a company's management quality?"
        ]
    }

@router.get("/health")
async def warren_buffett_health_check():
    """Health check for Warren Buffett chat agent."""
    try:
        # Test that we can import and initialize the agent
        from app.backend.services.warren_buffett_chat_agent import get_warren_buffett_agent
        agent = get_warren_buffett_agent()
        
        return {
            "status": "healthy",
            "agent": "warren_buffett",
            "tools_count": len(agent.tools),
            "model": agent.model_name,
            "provider": agent.model_provider
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "agent": "warren_buffett"
        } 