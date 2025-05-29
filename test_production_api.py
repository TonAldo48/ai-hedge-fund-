#!/usr/bin/env python3
"""
Simple test script for the deployed AI Hedge Fund API at api.aeero.io
"""

import requests
import json
import os
import urllib3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_BASE_URL = "https://api.aeero.io"
API_KEY = os.getenv("API_KEY") or os.getenv("HEDGE_FUND_API_KEY")

# Disable SSL warnings temporarily due to certificate propagation
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_health():
    """Test the health endpoint."""
    print("🔍 Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API is healthy! Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return False

def test_docs():
    """Test that documentation is accessible."""
    print("\n📚 Testing API Documentation...")
    try:
        response = requests.get(f"{API_BASE_URL}/docs", verify=False, timeout=10)
        if response.status_code == 200:
            print("✅ API documentation is accessible")
            print(f"   URL: {API_BASE_URL}/docs")
            return True
        else:
            print(f"❌ Documentation not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error accessing documentation: {e}")
        return False

def test_agents():
    """Test the agents endpoint."""
    print("\n🤖 Testing Available Agents...")
    try:
        response = requests.get(f"{API_BASE_URL}/hedge-fund/agents", verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            print(f"✅ Found {len(agents)} available agents")
            for agent in agents[:5]:  # Show first 5 agents
                print(f"   - {agent}")
            if len(agents) > 5:
                print(f"   ... and {len(agents) - 5} more")
            return True
        else:
            print(f"❌ Agents endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error fetching agents: {e}")
        return False

def test_authenticated_endpoint():
    """Test an authenticated endpoint."""
    if not API_KEY:
        print("\n⚠️  No API key found. Skipping authenticated test.")
        print("   Set API_KEY or HEDGE_FUND_API_KEY in your .env file to test authentication")
        return False
    
    print("\n🔑 Testing Authenticated Endpoint...")
    try:
        headers = {"X-API-Key": API_KEY}
        
        # Simple request to test authentication
        payload = {
            "tickers": ["AAPL"],
            "selected_agents": ["warren_buffett"],
            "model_name": "gpt-4o-mini",
            "model_provider": "OpenAI",
            "show_reasoning": False
        }
        
        response = requests.post(
            f"{API_BASE_URL}/hedge-fund/run-sync", 
            headers=headers,
            json=payload,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Authenticated request successful!")
            print(f"   Decisions: {len(data.get('decisions', []))}")
            print(f"   Authenticated: {data.get('metadata', {}).get('authenticated', False)}")
            if data.get('decisions'):
                decision = data['decisions'][0]
                print(f"   Sample Decision: {decision.get('action')} {decision.get('quantity')} shares of {decision.get('ticker')}")
            return True
        else:
            print(f"❌ Authenticated request failed: {response.status_code}")
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"   Error: {error_detail}")
            except:
                print(f"   Raw response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error with authenticated request: {e}")
        return False

def main():
    """Run all production tests."""
    print("🚀 AI Hedge Fund API - Production Deployment Test")
    print("=" * 60)
    print(f"API URL: {API_BASE_URL}")
    print(f"API Key configured: {'Yes' if API_KEY else 'No'}")
    print()
    
    # Run tests
    health_ok = test_health()
    docs_ok = test_docs()
    agents_ok = test_agents()
    auth_ok = test_authenticated_endpoint()
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print(f"   Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   Documentation: {'✅ PASS' if docs_ok else '❌ FAIL'}")
    print(f"   Agents Endpoint: {'✅ PASS' if agents_ok else '❌ FAIL'}")
    print(f"   Authentication: {'✅ PASS' if auth_ok else '❌ FAIL' if API_KEY else '⚠️  SKIPPED'}")
    
    if all([health_ok, docs_ok, agents_ok]) and (auth_ok or not API_KEY):
        print("\n🎉 Your API deployment is working great!")
        print(f"   🌐 Visit {API_BASE_URL}/docs to explore the API")
        if not API_KEY:
            print("   💡 Add an API key to test authenticated endpoints")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("\n📋 SSL Certificate Note:")
    print("   The SSL certificate may still be propagating.")
    print("   This is normal for new custom domains on Railway.")
    print("   The API is functional but using verify=False for now.")

if __name__ == "__main__":
    main() 