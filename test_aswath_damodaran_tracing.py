#!/usr/bin/env python3
"""
Test script for Aswath Damodaran agent with LangSmith tracing.

Tests the academic valuation strategy focusing on:
- Rigorous DCF analysis with FCFF projections
- Cost of equity calculation using CAPM
- Growth and reinvestment efficiency analysis
- Risk profile assessment (beta, leverage, coverage)
- Relative valuation cross-checks
- Margin of safety calculation

Usage: python test_aswath_damodaran_tracing.py
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.graph.state import AgentState
from src.agents.aswath_damodaran import aswath_damodaran_agent

def setup_langsmith():
    """Configure LangSmith for tracing"""
    # Set LangSmith environment variables
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_PROJECT"] = "ai-hedge-fund-damodaran-test"
    
    # Ensure LANGCHAIN_API_KEY is set
    if not os.environ.get("LANGCHAIN_API_KEY"):
        print("⚠️  Warning: LANGCHAIN_API_KEY not set. Tracing may not work properly.")
        print("   Set your LangSmith API key with: export LANGCHAIN_API_KEY=your_key_here")
    else:
        print("✅ LangSmith tracing configured")

def create_test_state():
    """
    Create test state for Aswath Damodaran analysis
    Using MSFT as it represents good academic valuation case study:
    - Established company with long financial history
    - Consistent cash flows for DCF modeling
    - Clear growth trends and risk metrics
    - Good for relative valuation comparisons
    """
    end_date = datetime.now() - timedelta(days=30)
    
    return {
        "data": {
            "tickers": ["MSFT"],  # Microsoft - excellent for DCF analysis
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

def run_damodaran_test():
    """Run Aswath Damodaran agent test with tracing"""
    print("🚀 Starting Aswath Damodaran Agent Test with LangSmith Tracing")
    print("=" * 65)
    
    # Setup tracing
    setup_langsmith()
    
    # Create test state
    state = create_test_state()
    ticker = state["data"]["tickers"][0]
    
    print(f"📊 Testing Damodaran academic valuation for {ticker}")
    print(f"📅 Analysis period: {state['data']['start_date']} to {state['data']['end_date']}")
    print()
    
    try:
        # Run the agent
        print("⚡ Executing Damodaran academic valuation analysis...")
        result = aswath_damodaran_agent(state)
        
        # Extract results
        damodaran_signals = result["data"]["analyst_signals"].get("aswath_damodaran_agent", {})
        
        if damodaran_signals:
            print("✅ Damodaran Analysis Complete!")
            print("=" * 65)
            
            for ticker, signal in damodaran_signals.items():
                print(f"\n📈 {ticker} - Damodaran Academic Valuation Analysis:")
                print(f"   🎯 Signal: {signal['signal'].upper()}")
                print(f"   📊 Confidence: {signal['confidence']:.1f}%")
                print(f"   💭 Reasoning: {signal['reasoning'][:250]}...")
                
        else:
            print("❌ No signals generated")
            
        # Display session information
        session_id = result.get("session_id") or state.get("session_id")
        if session_id:
            print(f"\n🔍 LangSmith Session ID: {session_id}")
            print(f"🌐 View traces at: https://smith.langchain.com/projects")
            
        print("\n" + "=" * 65)
        print("✅ Damodaran test completed successfully!")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during Damodaran analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("Aswath Damodaran Agent - Academic Valuation Test")
    print("Focus: DCF analysis, CAPM, growth/risk assessment")
    print("Strategy: Intrinsic value with rigorous margin of safety")
    print()
    
    result = run_damodaran_test()
    
    if result:
        print("\n🎉 Test completed! Check LangSmith dashboard for detailed traces.")
        print("📊 Key academic valuation metrics tracked:")
        print("   • Growth & Reinvestment (revenue CAGR, FCFF growth, ROIC)")
        print("   • Risk Profile (beta, debt/equity, interest coverage)")
        print("   • Intrinsic Value DCF (FCFF projections, CAPM discount rate)")
        print("   • Relative Valuation (P/E vs historical median)")
        print("   • Cost of Equity (CAPM: risk-free rate + beta × ERP)")
        print("   • Margin of Safety calculation")
    else:
        print("\n❌ Test failed. Check error messages above.") 