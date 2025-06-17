#!/usr/bin/env python3
"""
Test script for stanley_druckenmiller agent with LangSmith tracing.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.utils.tracing import setup_langsmith_tracing, get_tracing_enabled
from src.agents.stanley_druckenmiller import stanley_druckenmiller_agent
from src.graph.state import AgentState

def test_stanley_druckenmiller_with_tracing():
    """Test stanley_druckenmiller agent with tracing enabled."""
    
    print("🚀 Testing Stanley Druckenmiller Agent with LangSmith Tracing")
    print("=" * 60)
    
    # Setup tracing
    print("\n1. Setting up LangSmith tracing...")
    client = setup_langsmith_tracing(environment="development")
    
    if not get_tracing_enabled():
        print("⚠️  LangSmith tracing is not enabled.")
        print("   Continuing without tracing...")
    
    # Create test state
    print("\n2. Creating test analysis state...")
    test_ticker = "AMZN"  # Use Amazon as test case (growth momentum stock)
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = "2023-01-01"
    
    state = AgentState(
        messages=[],
        data={
            "tickers": [test_ticker],
            "end_date": end_date,
            "start_date": start_date,
            "analyst_signals": {}
        },
        metadata={
            "model_name": "gpt-4o-mini",
            "model_provider": "OpenAI", 
            "show_reasoning": True
        },
        session_id=f"test_stanley_druckenmiller_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    print(f"   📊 Analyzing ticker: {test_ticker}")
    print(f"   📅 End date: {end_date}")
    print(f"   📅 Start date: {start_date}")
    print(f"   🤖 Model: {state['metadata']['model_name']} ({state['metadata']['model_provider']})")
    print(f"   💭 Investment Style: macro_momentum_trading")
    
    # Run stanley_druckenmiller analysis
    print(f"\n3. Running Stanley Druckenmiller analysis for {test_ticker}...")
    try:
        result = stanley_druckenmiller_agent(state)
        
        print("✅ Analysis completed successfully!")
        
        # Display results
        if "analyst_signals" in result["data"] and "stanley_druckenmiller_agent" in result["data"]["analyst_signals"]:
            analysis = result["data"]["analyst_signals"]["stanley_druckenmiller_agent"][test_ticker]
            
            print(f"\n📈 Results for {test_ticker}:")
            print(f"   Signal: {analysis['signal'].upper()}")
            print(f"   Confidence: {analysis['confidence']:.1f}%") 
            print(f"   Reasoning: {analysis['reasoning'][:200]}...")
            
            if get_tracing_enabled():
                print(f"\n🔍 Tracing Information:")
                print(f"   Session ID: {state['session_id']}")
                print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'ai-hedge-fund-dev')}")
                print(f"   Investment Style: macro_momentum_trading")
                print(f"   Key Metrics: growth momentum, risk-reward, valuation, sentiment, insider activity")
                print(f"   Focus Areas: asymmetric opportunities, capital preservation, growth leaders")
                print(f"   Check your LangSmith dashboard for detailed traces!")
                print(f"   URL: https://smith.langchain.com/")
        
    except Exception as e:
        print(f"❌ Analysis failed: {str(e)}")
        print(f"   Make sure you have the required API keys configured")
        
        if get_tracing_enabled():
            print(f"   - Check LangSmith for error traces")
    
    print(f"\n4. Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    test_stanley_druckenmiller_with_tracing() 