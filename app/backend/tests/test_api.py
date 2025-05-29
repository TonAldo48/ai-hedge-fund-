#!/usr/bin/env python3
"""
Simple test script to verify the AI Hedge Fund API is working correctly.
Run this after starting the API server with: python app/backend/run_api.py
"""
import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30  # seconds

def test_api():
    """Run basic API tests."""
    print("🚀 Testing AI Hedge Fund API...\n")
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed:", response.json())
        else:
            print("❌ Health check failed:", response.status_code)
            return
    except Exception as e:
        print(f"❌ Could not connect to API at {BASE_URL}")
        print(f"   Error: {e}")
        print("\n💡 Make sure the API server is running with:")
        print("   python app/backend/run_api.py")
        return
    
    # Test 2: Get Available Agents
    print("\n2️⃣ Getting Available Agents...")
    response = requests.get(f"{BASE_URL}/hedge-fund/agents")
    if response.status_code == 200:
        agents = response.json()["agents"]
        print(f"✅ Found {len(agents)} available agents:")
        for agent in agents[:3]:  # Show first 3
            print(f"   - {agent['name']} (id: {agent['id']})")
        if len(agents) > 3:
            print(f"   ... and {len(agents) - 3} more")
    else:
        print("❌ Failed to get agents:", response.status_code)
        return
    
    # Test 3: Get Available Models
    print("\n3️⃣ Getting Available Models...")
    response = requests.get(f"{BASE_URL}/hedge-fund/models")
    if response.status_code == 200:
        models = response.json()["models"]
        print(f"✅ Found {len(models)} available models:")
        for model in models[:3]:  # Show first 3
            print(f"   - {model['display_name']} ({model['provider']})")
        if len(models) > 3:
            print(f"   ... and {len(models) - 3} more")
    else:
        print("❌ Failed to get models:", response.status_code)
        return
    
    # Test 4: Run Simple Analysis
    print("\n4️⃣ Running Simple Hedge Fund Analysis...")
    print("   (This may take 10-30 seconds depending on the model...)")
    
    # Prepare request
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    payload = {
        "tickers": ["AAPL", "MSFT"],  # Just 2 tickers for quick test
        "selected_agents": ["technical_analyst", "risk_analyst"],  # Just 2 agents
        "model_name": "gpt-4o-mini",  # Use smaller model for testing
        "model_provider": "OPENAI",
        "initial_cash": 50000,
        "margin_requirement": 0,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d")
    }
    
    print(f"\n   Request payload:")
    print(f"   - Tickers: {', '.join(payload['tickers'])}")
    print(f"   - Agents: {', '.join(payload['selected_agents'])}")
    print(f"   - Model: {payload['model_provider']}:{payload['model_name']}")
    print(f"   - Date Range: {payload['start_date']} to {payload['end_date']}")
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/hedge-fund/run-sync",
            json=payload,
            timeout=TEST_TIMEOUT
        )
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Analysis completed in {elapsed_time:.1f} seconds!")
            
            # Show decisions
            if "decisions" in result:
                print("\n📊 Trading Decisions:")
                decisions = result["decisions"]
                for ticker, decision in decisions.items():
                    print(f"\n   {ticker}:")
                    print(f"   - Action: {decision.get('action', 'N/A')}")
                    print(f"   - Quantity: {decision.get('quantity', 0)}")
                    print(f"   - Confidence: {decision.get('confidence', 0):.2%}")
                    if 'reasoning' in decision:
                        print(f"   - Reasoning: {decision['reasoning'][:100]}...")
            
            # Show metadata
            if "metadata" in result:
                print(f"\n📝 Metadata:")
                meta = result["metadata"]
                print(f"   - Model: {meta.get('model', 'N/A')}")
                print(f"   - Agents Used: {', '.join(meta.get('selected_agents', []))}")
        else:
            print(f"\n❌ Analysis failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"\n⏱️ Request timed out after {TEST_TIMEOUT} seconds")
        print("   Try using fewer tickers/agents or a faster model")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
    
    print("\n✅ API testing complete!")
    print("\n📚 Next steps:")
    print("   1. Import the Postman collection: app/backend/postman_collection.json")
    print("   2. Try the streaming endpoint: POST /hedge-fund/run")
    print("   3. Read the full documentation: app/backend/API_DOCUMENTATION.md")

if __name__ == "__main__":
    test_api() 