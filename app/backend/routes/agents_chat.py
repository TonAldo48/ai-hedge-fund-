"""
Unified API routes for all individual agent chat interfaces
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import json
import asyncio

from app.backend.models.schemas import ChatRequest, ChatResponse
from app.backend.middleware.auth import verify_api_key
from app.backend.services.streaming_adapter import LangChainToSSEAdapter

# Import all agent modules
from app.backend.services.warren_buffett_chat_agent import (
    get_warren_buffett_agent,
    process_warren_buffett_query
)
from app.backend.services.peter_lynch_chat_agent import (
    get_peter_lynch_agent,
    process_peter_lynch_query
)
from app.backend.services.charlie_munger_chat_agent import (
    get_charlie_munger_agent,
    process_charlie_munger_query
)
from app.backend.services.ben_graham_chat_agent import (
    get_ben_graham_agent,
    process_ben_graham_query
)
from app.backend.services.technical_analyst_chat_agent import (
    get_technical_analyst_agent,
    process_technical_analyst_query
)

router = APIRouter(prefix="/api/agents", tags=["agent-chat"])

# Available agents registry
AVAILABLE_AGENTS = {
    "warren_buffett": {
        "name": "Warren Buffett",
        "style": "Value Investing & Economic Moats",
        "get_agent": get_warren_buffett_agent,
        "process_query": process_warren_buffett_query
    },
    "peter_lynch": {
        "name": "Peter Lynch",
        "style": "Growth at Reasonable Price (GARP)",
        "get_agent": get_peter_lynch_agent,
        "process_query": process_peter_lynch_query
    },
    "charlie_munger": {
        "name": "Charlie Munger",
        "style": "Mental Models & Quality Business",
        "get_agent": get_charlie_munger_agent,
        "process_query": process_charlie_munger_query
    },
    "ben_graham": {
        "name": "Ben Graham",
        "style": "Deep Value & Margin of Safety",
        "get_agent": get_ben_graham_agent,
        "process_query": process_ben_graham_query
    },
    "technical_analyst": {
        "name": "Technical Analyst",
        "style": "Chart Patterns & Technical Indicators",
        "get_agent": get_technical_analyst_agent,
        "process_query": process_technical_analyst_query
    }
}

# Agent capabilities for discovery
AGENT_CAPABILITIES = {
    "warren_buffett": {
        "capabilities": ["moat_analysis", "intrinsic_value", "management_quality", "earnings_consistency"],
        "example_queries": [
            "What's Apple's competitive moat?",
            "Calculate the intrinsic value of Microsoft",
            "Is Tesla's management shareholder-friendly?",
            "How consistent are Amazon's earnings?"
        ]
    },
    "peter_lynch": {
        "capabilities": ["growth_analysis", "peg_ratio", "fundamentals", "sentiment", "insider_activity"],
        "example_queries": [
            "What's Tesla's PEG ratio?",
            "Is Apple still a growth stock?",
            "Find me a ten-bagger opportunity",
            "How's the insider activity for NVDA?"
        ]
    },
    "charlie_munger": {
        "capabilities": ["moat_analysis", "management_quality", "predictability", "mental_models"],
        "example_queries": [
            "Does Coca-Cola have a strong moat?",
            "What mental models apply to Amazon?",
            "How predictable are Microsoft's earnings?",
            "Analyze Apple using inversion principle"
        ]
    },
    "ben_graham": {
        "capabilities": ["earnings_stability", "financial_strength", "margin_of_safety", "graham_number"],
        "example_queries": [
            "What's Apple's margin of safety?",
            "Is this stock undervalued by Graham standards?",
            "Calculate the Graham Number for MSFT",
            "How's the financial strength of GOOGL?"
        ]
    },
    "technical_analyst": {
        "capabilities": ["trend_analysis", "momentum", "support_resistance", "chart_patterns"],
        "example_queries": [
            "What do the charts say about Tesla?",
            "Is this a good entry point for Apple?",
            "What's the trend for Bitcoin?",
            "Where are the support levels for SPY?"
        ]
    }
}

@router.get("/")
async def get_available_agents(api_key: str = Depends(verify_api_key)):
    """Get all available chat agents and their capabilities."""
    agents = []
    for agent_id, agent_info in AVAILABLE_AGENTS.items():
        agent_data = {
            "id": agent_id,
            "name": agent_info["name"],
            "style": agent_info["style"],
            "capabilities": AGENT_CAPABILITIES.get(agent_id, {}).get("capabilities", []),
            "example_queries": AGENT_CAPABILITIES.get(agent_id, {}).get("example_queries", [])
        }
        agents.append(agent_data)
    
    return {
        "agents": agents,
        "total": len(agents)
    }

@router.post("/{agent_name}/analyze")
async def analyze_with_agent(
    agent_name: str,
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Universal endpoint for any agent chat analysis.
    
    Args:
        agent_name: The agent to use (e.g., 'warren_buffett', 'peter_lynch')
        request: Chat request with query and optional chat history
        
    Returns:
        Agent's analysis and response
    """
    if agent_name not in AVAILABLE_AGENTS:
        raise HTTPException(
            status_code=404, 
            detail=f"Agent '{agent_name}' not found. Available agents: {list(AVAILABLE_AGENTS.keys())}"
        )
    
    try:
        # Get the process function for this agent
        process_func = AVAILABLE_AGENTS[agent_name]["process_query"]
        
        # Process the query
        result = await process_func(request.message, request.chat_history)
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_name}/analyze-streaming")
async def stream_agent_analysis(
    agent_name: str,
    request: ChatRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Universal streaming endpoint for any agent.
    
    Args:
        agent_name: The agent to use
        request: Chat request with query and optional chat history
        
    Returns:
        Streaming response with real-time analysis updates
    """
    if agent_name not in AVAILABLE_AGENTS:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{agent_name}' not found. Available agents: {list(AVAILABLE_AGENTS.keys())}"
        )
    
    try:
        # Get the agent instance
        get_agent_func = AVAILABLE_AGENTS[agent_name]["get_agent"]
        agent = get_agent_func()
        
        # Create the streaming generator with proper SSE formatting
        async def event_generator():
            # Get the raw LangChain events
            langchain_events = agent.analyze_streaming(request.message, request.chat_history)
            
            # Convert to SSE format using our adapter
            async for sse_event in LangChainToSSEAdapter.convert_to_sse(
                langchain_events, 
                include_reasoning=True
            ):
                yield sse_event
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare")
async def compare_agent_perspectives(
    request: Dict[str, Any],
    api_key: str = Depends(verify_api_key)
):
    """
    Get multiple agent perspectives on the same query.
    
    Request body:
    {
        "query": "Should I invest in Apple?",
        "selected_agents": ["warren_buffett", "peter_lynch", "technical_analyst"]
    }
    """
    query = request.get("query")
    selected_agents = request.get("selected_agents", [])
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    if not selected_agents:
        raise HTTPException(status_code=400, detail="At least one agent must be selected")
    
    # Validate agents
    invalid_agents = [a for a in selected_agents if a not in AVAILABLE_AGENTS]
    if invalid_agents:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agents: {invalid_agents}. Available: {list(AVAILABLE_AGENTS.keys())}"
        )
    
    try:
        # Run all agent analyses in parallel
        tasks = []
        for agent_name in selected_agents:
            process_func = AVAILABLE_AGENTS[agent_name]["process_query"]
            tasks.append(process_func(query))
        
        results = await asyncio.gather(*tasks)
        
        # Format responses
        agent_responses = {}
        for i, agent_name in enumerate(selected_agents):
            agent_responses[agent_name] = {
                "name": AVAILABLE_AGENTS[agent_name]["name"],
                "response": results[i]["response"],
                "timestamp": results[i]["timestamp"]
            }
        
        return {
            "query": query,
            "agent_responses": agent_responses,
            "response_count": len(agent_responses)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommend")
async def recommend_best_agent(
    query: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Recommend the best agent based on the query content.
    
    Args:
        query: The investment question
        
    Returns:
        Recommended agent and reasoning
    """
    query_lower = query.lower()
    
    # Keywords mapping to agents
    agent_keywords = {
        "warren_buffett": ["moat", "intrinsic value", "buffett", "berkshire", "long-term", "quality", "management"],
        "peter_lynch": ["growth", "peg", "ten-bagger", "lynch", "garp", "earnings growth"],
        "charlie_munger": ["mental model", "munger", "predictable", "quality business", "psychology", "invert"],
        "ben_graham": ["margin of safety", "graham", "undervalued", "net-net", "deep value", "conservative"],
        "technical_analyst": ["chart", "technical", "trend", "support", "resistance", "momentum", "indicator"]
    }
    
    # Score each agent based on keyword matches
    scores = {}
    for agent, keywords in agent_keywords.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        scores[agent] = score
    
    # Get the best agent
    best_agent = max(scores.keys(), key=lambda k: scores[k])
    
    # If no clear winner, use Warren Buffett as default
    if scores[best_agent] == 0:
        best_agent = "warren_buffett"
        reasoning = "No specific investment style detected, defaulting to Warren Buffett for comprehensive value analysis."
    else:
        reasoning = f"Query contains keywords related to {AVAILABLE_AGENTS[best_agent]['name']}'s investment style."
    
    return {
        "recommended_agent": best_agent,
        "agent_name": AVAILABLE_AGENTS[best_agent]["name"],
        "agent_style": AVAILABLE_AGENTS[best_agent]["style"],
        "reasoning": reasoning,
        "confidence": min(scores[best_agent] / 3, 1.0)  # Normalize to 0-1
    } 