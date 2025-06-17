#!/usr/bin/env python3
"""
Test script for Warren Buffett agent with multiple tickers and LangSmith tracing.

This script runs analysis on multiple stocks to demonstrate
how LangSmith tracing captures multiple analyses in one session.
"""

import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.utils.tracing import setup_langsmith_tracing, get_tracing_enabled
from src.agents.warren_buffett import warren_buffett_agent
from src.graph.state import AgentState

def test_warren_buffett_multiple_tickers():
    """Test Warren Buffett agent with multiple tickers and tracing enabled."""
    
    print("🚀 Testing Warren Buffett Agent with Multiple Tickers")
    print("=" * 70)
    
    # Setup tracing
    print("\n1. Setting up LangSmith tracing...")
    client = setup_langsmith_tracing(environment="development")
    
    if not get_tracing_enabled():
        print("⚠️  LangSmith tracing is not enabled.")
        print("   Continuing without tracing...")
    
    # Test with multiple tickers
    print("\n2. Creating multi-ticker analysis state...")
    test_tickers = ["AAPL", "MSFT", "NVDA"]  # Apple, Microsoft, NVDA
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    state = AgentState(
        messages=[],
        data={
            "tickers": test_tickers,
            "end_date": end_date,
            "start_date": "2025-00-01",
            "analyst_signals": {}
        },
        metadata={
            "model_name": "gpt-4o",  # Use a commonly available model
            "model_provider": "OpenAI",
            "show_reasoning": True
        },
        session_id=f"multi_test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    print(f"   📊 Analyzing tickers: {', '.join(test_tickers)}")
    print(f"   📅 End date: {end_date}")
    print(f"   🤖 Model: {state['metadata']['model_name']} ({state['metadata']['model_provider']})")
    
    # Run Warren Buffett analysis on multiple tickers
    print(f"\n3. Running Warren Buffett analysis on {len(test_tickers)} tickers...")
    try:
        result = warren_buffett_agent(state)
        
        print("✅ Multi-ticker analysis completed successfully!")
        
        # Display results for each ticker
        if "analyst_signals" in result["data"] and "warren_buffett_agent" in result["data"]["analyst_signals"]:
            analyses = result["data"]["analyst_signals"]["warren_buffett_agent"]
            
            print(f"\n📈 Results Summary:")
            print("=" * 50)
            
            for ticker in test_tickers:
                if ticker in analyses:
                    analysis = analyses[ticker]
                    
                    print(f"\n🏢 {ticker}:")
                    print(f"   Signal: {analysis['signal'].upper()}")
                    print(f"   Confidence: {analysis['confidence']:.1f}%")
                    print(f"   Reasoning: {analysis['reasoning'][:150]}...")
                    
                    # Show signal distribution
                    signal_emoji = {
                        "bullish": "📈🟢",
                        "bearish": "📉🔴", 
                        "neutral": "📊🟡"
                    }
                    print(f"   {signal_emoji.get(analysis['signal'], '❓')} {analysis['signal'].title()}")
            
            # Summary statistics
            signals = [analyses[ticker]['signal'] for ticker in test_tickers if ticker in analyses]
            signal_counts = {s: signals.count(s) for s in ['bullish', 'bearish', 'neutral']}
            
            print(f"\n📊 Portfolio Signal Distribution:")
            print(f"   🟢 Bullish: {signal_counts.get('bullish', 0)}")
            print(f"   🔴 Bearish: {signal_counts.get('bearish', 0)}")
            print(f"   🟡 Neutral: {signal_counts.get('neutral', 0)}")
            
            avg_confidence = sum(analyses[ticker]['confidence'] for ticker in test_tickers if ticker in analyses) / len(test_tickers)
            print(f"   📊 Average Confidence: {avg_confidence:.1f}%")
            
            if get_tracing_enabled():
                print(f"\n🔍 Tracing Information:")
                print(f"   Session ID: {state['session_id']}")
                print(f"   Project: {os.getenv('LANGCHAIN_PROJECT', 'ai-hedge-fund-dev')}")
                print(f"   Tickers Analyzed: {len(test_tickers)}")
                print(f"   Total LLM Calls: ~{len(test_tickers) * 6}")  # Each ticker makes ~6 traced function calls
                print(f"   Check your LangSmith dashboard for detailed traces!")
                print(f"   URL: https://smith.langchain.com/")
                print(f"\n   💡 Look for traces with these tags:")
                print(f"      - hedge_fund, value_investing, buffett")
                print(f"      - fundamental_analysis, moat, valuation")
        
    except Exception as e:
        print(f"❌ Multi-ticker analysis failed: {str(e)}")
        print(f"   Make sure you have the required API keys configured")
        
        if get_tracing_enabled():
            print(f"   - Check LangSmith for error traces")
    
    print(f"\n4. Multi-ticker test completed!")
    print("=" * 70)

if __name__ == "__main__":
    test_warren_buffett_multiple_tickers() 