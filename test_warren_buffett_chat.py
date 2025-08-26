#!/usr/bin/env python3
"""
Test script for Warren Buffett Chat Agent
"""
import asyncio
import json
import requests
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
WARREN_BUFFETT_ENDPOINT = f"{BASE_URL}/warren-buffett/analyze"
CAPABILITIES_ENDPOINT = f"{BASE_URL}/warren-buffett/capabilities"
HEALTH_ENDPOINT = f"{BASE_URL}/warren-buffett/health"

def test_health_check():
    """Test Warren Buffett agent health check."""
    print("🏥 Testing Warren Buffett agent health check...")
    
    try:
        response = requests.get(HEALTH_ENDPOINT)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Health check passed: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_capabilities():
    """Test Warren Buffett agent capabilities endpoint."""
    print("\n🔍 Testing Warren Buffett agent capabilities...")
    
    try:
        response = requests.get(CAPABILITIES_ENDPOINT)
        response.raise_for_status()
        
        result = response.json()
        print(f"✅ Capabilities retrieved successfully")
        print(f"📊 Agent: {result['agent']}")
        print(f"📋 Capabilities: {len(result['capabilities'])} analysis types")
        print(f"💡 Example queries: {len(result['example_queries'])} examples")
        
        return True
        
    except Exception as e:
        print(f"❌ Capabilities test failed: {str(e)}")
        return False

def test_warren_buffett_analysis(query: str, description: str):
    """Test a specific Warren Buffett analysis query."""
    print(f"\n🧠 Testing: {description}")
    print(f"📝 Query: {query}")
    
    try:
        payload = {
            "query": query,
            "chat_history": []
        }
        
        response = requests.post(
            WARREN_BUFFETT_ENDPOINT, 
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        result = response.json()
        
        if result["success"]:
            print(f"✅ Analysis successful")
            print(f"🎯 Agent: {result['agent']}")
            print(f"📊 Response length: {len(result['response'])} characters")
            print(f"🔧 Tools used: {len(result.get('intermediate_steps', []))} steps")
            print(f"💬 Warren Buffett says: {result['response'][:200]}...")
            return True
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def main():
    """Run all Warren Buffett chat agent tests."""
    print("🚀 Starting Warren Buffett Chat Agent Tests")
    print("=" * 60)
    
    # Test health check
    health_ok = test_health_check()
    if not health_ok:
        print("❌ Health check failed, stopping tests")
        return
    
    # Test capabilities
    capabilities_ok = test_capabilities()
    if not capabilities_ok:
        print("❌ Capabilities test failed, stopping tests")
        return
    
    # Test various Warren Buffett analysis queries
    test_cases = [
        {
            "query": "What do you think about Apple's competitive moat?",
            "description": "Competitive Moat Analysis"
        },
        {
            "query": "How strong are Microsoft's fundamentals?", 
            "description": "Fundamentals Analysis"
        },
        {
            "query": "What's Tesla's intrinsic value and margin of safety?",
            "description": "Intrinsic Value Analysis"
        },
        {
            "query": "How well does Amazon's management allocate capital?",
            "description": "Management Quality Analysis"
        },
        {
            "query": "Are Berkshire Hathaway's earnings consistent?",
            "description": "Earnings Consistency Analysis"
        }
    ]
    
    success_count = 0
    total_tests = len(test_cases)
    
    for test_case in test_cases:
        success = test_warren_buffett_analysis(
            test_case["query"], 
            test_case["description"]
        )
        if success:
            success_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🎯 Warren Buffett Chat Agent Test Summary")
    print(f"✅ Successful tests: {success_count}/{total_tests}")
    print(f"📊 Success rate: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Warren Buffett agent is working perfectly.")
    else:
        print("⚠️  Some tests failed. Check the logs above for details.")

if __name__ == "__main__":
    main() 