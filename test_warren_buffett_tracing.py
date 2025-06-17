#!/usr/bin/env python3
"""
Test script for Warren Buffett agent with LangSmith tracing.

This script runs a sample analysis on a single ticker to demonstrate
LangSmith tracing functionality.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.utils.tracing import setup_langsmith_tracing, get_tracing_enabled
from src.agents.warren_buffett import warren_buffett_agent
from src.graph.state import AgentState

def test_warren_buffett_with_tracing():
    """Test Warren Buffett agent with tracing enabled."""
    
    print("🚀 Testing Warren Buffett Agent with LangSmith Tracing")
    print("=" * 60)
    
    # Setup tracing
    print("\n1. Setting up LangSmith tracing...")
    client = setup_langsmith_tracing(environment="development")
    
    if not get_tracing_enabled():
        print("⚠️  LangSmith tracing is not enabled.")
        print("   To enable tracing, set the following environment variables:")
        print("   - LANGCHAIN_TRACING_V2=true")
        print("   - LANGCHAIN_API_KEY=your_langsmith_api_key")
        print("   \n   Continuing without tracing...")
    
    # Create test state
    print("\n2. Creating test analysis state...")
    test_ticker = "AAPL"  # Use Apple as test case
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    state = AgentState(
        messages=[],
        data={
            "tickers": [test_ticker],
            "end_date": end_date,
            "start_date": "2023-01-01",
            "analyst_signals": {}
        },
        metadata={
            "model_name": "gpt-4o-mini",  # Use a commonly available model
            "model_provider": "OpenAI",
            "show_reasoning": True
        },
        session_id=f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    print(f"   📊 Analyzing ticker: {test_ticker}")
    print(f"   📅 End date: {end_date}")
    print(f"   🤖 Model: {state['metadata']['model_name']} ({state['metadata']['model_provider']})")
    
    # Run Warren Buffett analysis
    print(f"\n3. Running Warren Buffett analysis for {test_ticker}...")
    try:
        result = warren_buffett_agent(state)
        
        print("✅ Analysis completed successfully!")
        
        # Display results
        if "analyst_signals" in result["data"] and "warren_buffett_agent" in result["data"]["analyst_signals"]:
            analysis = result["data"]["analyst_signals"]["warren_buffett_agent"][test_ticker]
            
            print(f"\n📈 Results for {test_ticker}:")
            print(f"   Signal: {analysis['signal'].upper()}")
            print(f"   Confidence: {analysis['confidence']:.1f}%") 
            print(f"   Reasoning: {analysis['reasoning'][:200]}...")
            
            if get_tracing_enabled():
                print(f"\n🔍 Tracing Information:")
                print(f"   Session ID: {state['session_id']}")
                print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'ai-hedge-fund')}")
                print(f"   Check your LangSmith dashboard for detailed traces!")
                print(f"   URL: https://smith.langchain.com/")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        print(f"   Make sure you have the required API keys configured:")
        print(f"   - OpenAI API key for LLM calls")
        print(f"   - Financial data API access")
        
        if get_tracing_enabled():
            print(f"   - Check LangSmith for error traces")
    
    print(f"\n4. Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_warren_buffett_with_tracing() 