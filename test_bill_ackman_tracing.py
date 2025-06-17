#!/usr/bin/env python3
"""
Test script for bill_ackman agent with LangSmith tracing.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.utils.tracing import setup_langsmith_tracing, get_tracing_enabled
from src.agents.bill_ackman import bill_ackman_agent
from src.graph.state import AgentState

def test_bill_ackman_with_tracing():
    """Test bill_ackman agent with tracing enabled."""
    
    print("🚀 Testing Bill Ackman Agent with LangSmith Tracing")
    print("=" * 60)
    
    # Setup tracing
    print("\n1. Setting up LangSmith tracing...")
    client = setup_langsmith_tracing(environment="development")
    
    if not get_tracing_enabled():
        print("⚠️  LangSmith tracing is not enabled.")
        print("   Continuing without tracing...")
    
    # Create test state
    print("\n2. Creating test analysis state...")
    test_ticker = "SBUX"  # Use Starbucks as test case (brand-focused company)
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
        session_id=f"test_bill_ackman_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    print(f"   📊 Analyzing ticker: {test_ticker}")
    print(f"   📅 End date: {end_date}")
    print(f"   📅 Start date: {start_date}")
    print(f"   🤖 Model: {state['metadata']['model_name']} ({state['metadata']['model_provider']})")
    print(f"   💭 Investment Style: activist_value_investing")
    
    # Run bill_ackman analysis
    print(f"\n3. Running Bill Ackman analysis for {test_ticker}...")
    try:
        result = bill_ackman_agent(state)
        
        print("✅ Analysis completed successfully!")
        
        # Display results
        if "analyst_signals" in result["data"] and "bill_ackman_agent" in result["data"]["analyst_signals"]:
            analysis = result["data"]["analyst_signals"]["bill_ackman_agent"][test_ticker]
            
            print(f"\n📈 Results for {test_ticker}:")
            print(f"   Signal: {analysis['signal'].upper()}")
            print(f"   Confidence: {analysis['confidence']:.1f}%") 
            print(f"   Reasoning: {analysis['reasoning'][:200]}...")
            
            if get_tracing_enabled():
                print(f"\n🔍 Tracing Information:")
                print(f"   Session ID: {state['session_id']}")
                print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'ai-hedge-fund-dev')}")
                print(f"   Investment Style: activist_value_investing")
                print(f"   Key Metrics: quality, balance sheet, activism potential, valuation")
                print(f"   Focus Areas: durable brands, capital discipline, operational improvements")
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
    test_bill_ackman_with_tracing() 