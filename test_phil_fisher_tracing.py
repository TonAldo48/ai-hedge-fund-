#!/usr/bin/env python3
"""
Test script for Phil Fisher agent with LangSmith tracing.

Tests the quality growth investing strategy focusing on:
- Long-term growth potential and R&D investment
- Management quality and margin consistency  
- Balanced approach to valuation (willing to pay for quality)
- Emphasis on sustainable competitive advantages

Usage: python test_phil_fisher_tracing.py
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.state import AgentState
from src.agents.phil_fisher import phil_fisher_agent

def setup_langsmith():
    """Configure LangSmith for tracing"""
    # Set LangSmith environment variables
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "ai-hedge-fund-phil-fisher-test"
    
    # Ensure LANGCHAIN_API_KEY is set
    if not os.environ.get("LANGCHAIN_API_KEY"):
        print("⚠️  Warning: LANGCHAIN_API_KEY not set. Tracing may not work properly.")
        print("   Set your LangSmith API key with: export LANGCHAIN_API_KEY=your_key_here")
    else:
        print("✅ LangSmith tracing configured")

def create_test_state():
    """
    Create test state for Phil Fisher analysis
    Using AMZN as it represents Fisher's ideal:
    - Long-term growth story with R&D investment
    - Strong margins and market leadership
    - Management that thinks long-term
    - Willing to sacrifice short-term profits for growth
    """
    end_date = datetime.now() - timedelta(days=30)
    
    return {
        "data": {
            "tickers": ["AMZN"],  # Amazon - classic Fisher-style growth company
            "end_date": end_date.strftime("%Y-%m-%d"),
            "start_date": (end_date - timedelta(days=365)).strftime("%Y-%m-%d"),
            "analyst_signals": {}
        },
        "metadata": {
            "model_name": "gpt-4o-mini",
            "model_provider": "openai", 
            "show_reasoning": True
        },
        "messages": []
    }

def run_phil_fisher_test():
    """Run Phil Fisher agent test with tracing"""
    print("🚀 Starting Phil Fisher Agent Test with LangSmith Tracing")
    print("=" * 60)
    
    # Setup tracing
    setup_langsmith()
    
    # Create test state
    state = create_test_state()
    ticker = state["data"]["tickers"][0]
    
    print(f"📊 Testing Phil Fisher analysis for {ticker}")
    print(f"📅 Analysis period: {state['data']['start_date']} to {state['data']['end_date']}")
    print()
    
    try:
        # Run the agent
        print("⚡ Executing Phil Fisher quality growth analysis...")
        result = phil_fisher_agent(state)
        
        # Extract results
        phil_fisher_signals = result["data"]["analyst_signals"].get("phil_fisher_agent", {})
        
        if phil_fisher_signals:
            print("✅ Phil Fisher Analysis Complete!")
            print("=" * 60)
            
            for ticker, signal in phil_fisher_signals.items():
                print(f"\n📈 {ticker} - Phil Fisher Quality Growth Analysis:")
                print(f"   🎯 Signal: {signal['signal'].upper()}")
                print(f"   📊 Confidence: {signal['confidence']:.1f}%")
                print(f"   💭 Reasoning: {signal['reasoning'][:200]}...")
                
        else:
            print("❌ No signals generated")
            
        # Display session information
        session_id = result.get("session_id") or state.get("session_id")
        if session_id:
            print(f"\n🔍 LangSmith Session ID: {session_id}")
            print(f"🌐 View traces at: https://smith.langchain.com/projects")
            
        print("\n" + "=" * 60)
        print("✅ Phil Fisher test completed successfully!")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during Phil Fisher analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Phil Fisher Agent - Quality Growth Investing Test")
    print("Focus: Long-term growth, R&D investment, management quality")
    print("Strategy: Buy exceptional companies with sustainable advantages")
    print()
    
    result = run_phil_fisher_test()
    
    if result:
        print("\n🎉 Test completed! Check LangSmith dashboard for detailed traces.")
        print("📊 Key metrics tracked:")
        print("   • Growth Quality (revenue/EPS growth, R&D investment)")
        print("   • Margins Stability (operating/gross margin consistency)")  
        print("   • Management Efficiency (ROE, debt management, FCF)")
        print("   • Fisher Valuation (P/E, P/FCF with growth premium)")
        print("   • Insider Activity & Sentiment")
    else:
        print("\n❌ Test failed. Check error messages above.") 