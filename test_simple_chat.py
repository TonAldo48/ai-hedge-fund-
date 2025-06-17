#!/usr/bin/env python3
"""
Simple test for the natural language financial analysis chat agent.
Tests the specific query: "How does Tesla's valuation look from a Peter Lynch perspective?"
"""
import asyncio
import os
from pathlib import Path
import sys

# Add parent directory to path so we can import from 'src'
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

async def test_tesla_lynch_query():
    """Test the specific Tesla query using Peter Lynch's approach."""
    print("🧪 Testing Tesla Valuation Analysis (Peter Lynch Perspective)")
    print("=" * 60)
    
    try:
        # Import here to avoid module-level initialization issues
        from app.backend.services.chat_agent import FinancialAnalysisAgent
        
        # Check if we have required models available
        from src.llm.models import get_model
        
        # Try different models in order of preference
        model_configs = [
            ("gpt-4o-mini", "openai"),
            ("gpt-4", "openai"), 
            ("claude-3-5-sonnet-20241022", "anthropic"),
            ("deepseek-chat", "deepseek")
        ]
        
        agent = None
        for model_name, model_provider in model_configs:
            try:
                print(f"🤖 Trying model: {model_name} ({model_provider})")
                test_llm = get_model(model_name, model_provider)
                if test_llm is not None:
                    agent = FinancialAnalysisAgent(model_name, model_provider)
                    break
            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")
                continue
        
        if agent is None:
            print("❌ No working LLM model found. Please configure API keys.")
            return None
        
        print(f"✅ Using model: {agent.model_name} ({agent.model_provider})")
        
        # Test query
        query = "How does Tesla's valuation look from a Peter Lynch perspective?"
        print(f"\n📝 Query: {query}")
        print("🔄 Processing...")
        
        # Run analysis
        result = await agent.analyze(query)
        
        print(f"\n{'='*60}")
        print(f"📊 RESULTS")
        print(f"{'='*60}")
        print(f"✅ Success: {result['success']}")
        
        if result['success']:
            print(f"\n🎯 Analysis Response:")
            print(f"{result['response']}")
            
            if 'intermediate_steps' in result and result['intermediate_steps']:
                print(f"\n🔍 Tools Used:")
                for i, (action, observation) in enumerate(result['intermediate_steps'], 1):
                    print(f"  {i}. {action.tool}: {action.tool_input}")
        else:
            print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_direct_function_call():
    """Test calling Peter Lynch valuation function directly."""
    print("\n" + "="*60)
    print("🔧 Testing Direct Function Call (Peter Lynch Valuation)")
    print("="*60)
    
    try:
        from src.agents.peter_lynch import analyze_lynch_valuation
        from src.tools.api import search_line_items, get_market_cap
        from datetime import datetime
        
        ticker = "TSLA"
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"📈 Fetching data for {ticker}...")
        
        # Fetch required data
        line_items = search_line_items(
            ticker,
            [
                "earnings_per_share", "revenue", "net_income", "outstanding_shares",
                "book_value_per_share", "dividends_and_other_cash_distributions"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        market_cap = get_market_cap(ticker, end_date)
        
        print(f"✅ Data fetched successfully")
        print(f"   Market Cap: ${market_cap:,.0f}" if market_cap else "   Market Cap: N/A")
        print(f"   Financial Records: {len(line_items) if line_items else 0}")
        
        # Run analysis
        print(f"\n🔍 Running Peter Lynch valuation analysis...")
        result = analyze_lynch_valuation(line_items, market_cap)
        
        print(f"\n📊 Results:")
        print(f"   Score: {result.get('score', 'N/A')}/{result.get('max_score', 'N/A')}")
        print(f"   Details: {result.get('details', 'N/A')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Direct function test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run tests."""
    print("🚀 Natural Language Financial Analysis Test")
    print("Testing: 'How does Tesla's valuation look from a Peter Lynch perspective?'")
    print("=" * 80)
    
    # Test 1: Direct function call
    direct_result = await test_direct_function_call()
    
    # Test 2: Natural language agent
    agent_result = await test_tesla_lynch_query()
    
    print("\n" + "="*80)
    print("📋 TEST SUMMARY")
    print("="*80)
    print(f"Direct Function Call: {'✅ Pass' if direct_result else '❌ Fail'}")
    print(f"Natural Language Agent: {'✅ Pass' if agent_result and agent_result.get('success') else '❌ Fail'}")
    
    if agent_result and agent_result.get('success'):
        print(f"\n🎯 SUCCESS! The agent:")
        print(f"   • Understood the query about Tesla's valuation")
        print(f"   • Identified Peter Lynch's investment approach")
        print(f"   • Called the appropriate analysis functions")
        print(f"   • Generated a natural language response")
        print(f"\n💡 You can now use natural language to analyze any stock!")

if __name__ == "__main__":
    asyncio.run(main()) 