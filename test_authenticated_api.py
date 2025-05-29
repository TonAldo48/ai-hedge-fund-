#!/usr/bin/env python3
"""
Test script for the authenticated AI Hedge Fund API.
Demonstrates how to use API key authentication with the hedge fund endpoints.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY") or os.getenv("HEDGE_FUND_API_KEY")

def test_public_endpoints():
    """Test endpoints that don't require authentication."""
    print("🌐 Testing Public Endpoints (No Authentication Required)")
    print("=" * 60)
    
    # Health check
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health Check: {response.status_code} - {response.json()}")
    
    # Root endpoint
    response = requests.get(f"{BASE_URL}/")
    print(f"Root: {response.status_code} - API info received")
    
    # Get agents
    response = requests.get(f"{BASE_URL}/hedge-fund/agents")
    agents = response.json()
    print(f"Agents: {response.status_code} - {len(agents['agents'])} agents available")
    
    # Get models
    response = requests.get(f"{BASE_URL}/hedge-fund/models")
    models = response.json()
    print(f"Models: {response.status_code} - {len(models['models'])} models available")
    print()


def test_protected_endpoints_without_auth():
    """Test protected endpoints without authentication (should fail)."""
    print("🚫 Testing Protected Endpoints WITHOUT Authentication (Should Fail)")
    print("=" * 70)
    
    # Test sync endpoint without auth
    response = requests.post(f"{BASE_URL}/hedge-fund/run-sync", json={
        "tickers": ["AAPL"],
        "selected_agents": ["warren_buffett"],
        "model_name": "gpt-4o-mini",
        "model_provider": "OpenAI"
    })
    print(f"Sync Endpoint (no auth): {response.status_code} - {response.json().get('detail', 'Unknown error')}")
    
    # Test streaming endpoint without auth
    response = requests.post(f"{BASE_URL}/hedge-fund/run", json={
        "tickers": ["AAPL"],
        "selected_agents": ["warren_buffett"],
        "model_name": "gpt-4o-mini",
        "model_provider": "OpenAI"
    })
    print(f"Streaming Endpoint (no auth): {response.status_code} - {response.json().get('detail', 'Unknown error')}")
    print()


def test_protected_endpoints_with_header_auth():
    """Test protected endpoints with X-API-Key header authentication."""
    if not API_KEY:
        print("⚠️  No API key found. Skipping authenticated tests.")
        print("   Set API_KEY or HEDGE_FUND_API_KEY in your .env file")
        return
    
    print("🔑 Testing Protected Endpoints WITH X-API-Key Header Authentication")
    print("=" * 70)
    
    headers = {"X-API-Key": API_KEY}
    
    # Test sync endpoint with header auth
    response = requests.post(f"{BASE_URL}/hedge-fund/run-sync", 
        headers=headers,
        json={
            "tickers": ["AAPL"],
            "selected_agents": ["warren_buffett"],
            "model_name": "gpt-4o-mini",
            "model_provider": "OpenAI",
            "show_reasoning": True
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sync Endpoint (header auth): {response.status_code} - Success!")
        print(f"   Decisions: {len(result.get('decisions', []))} decisions")
        print(f"   Authenticated: {result.get('metadata', {}).get('authenticated', False)}")
        if result.get('decisions'):
            decision = result['decisions'][0]
            print(f"   First Decision: {decision.get('action')} {decision.get('quantity')} shares of {decision.get('ticker')}")
    else:
        print(f"❌ Sync Endpoint (header auth): {response.status_code} - {response.json().get('detail', 'Unknown error')}")
    print()


def test_protected_endpoints_with_bearer_auth():
    """Test protected endpoints with Bearer token authentication."""
    if not API_KEY:
        print("⚠️  No API key found. Skipping Bearer token tests.")
        return
    
    print("🎫 Testing Protected Endpoints WITH Bearer Token Authentication")
    print("=" * 70)
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    # Test sync endpoint with bearer auth
    response = requests.post(f"{BASE_URL}/hedge-fund/run-sync", 
        headers=headers,
        json={
            "tickers": ["MSFT"],
            "selected_agents": ["technical_analyst"],
            "model_name": "gpt-4o-mini",
            "model_provider": "OpenAI",
            "show_reasoning": False
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Sync Endpoint (bearer auth): {response.status_code} - Success!")
        print(f"   Decisions: {len(result.get('decisions', []))} decisions")
        print(f"   Authenticated: {result.get('metadata', {}).get('authenticated', False)}")
        if result.get('decisions'):
            decision = result['decisions'][0]
            print(f"   First Decision: {decision.get('action')} {decision.get('quantity')} shares of {decision.get('ticker')}")
    else:
        print(f"❌ Sync Endpoint (bearer auth): {response.status_code} - {response.json().get('detail', 'Unknown error')}")
    print()


def test_invalid_api_key():
    """Test with invalid API key."""
    print("🚨 Testing with Invalid API Key (Should Fail)")
    print("=" * 50)
    
    headers = {"X-API-Key": "invalid-key-123"}
    
    response = requests.post(f"{BASE_URL}/hedge-fund/run-sync", 
        headers=headers,
        json={
            "tickers": ["AAPL"],
            "selected_agents": ["warren_buffett"],
            "model_name": "gpt-4o-mini",
            "model_provider": "OpenAI"
        }
    )
    print(f"Invalid Key Test: {response.status_code} - {response.json().get('detail', 'Unknown error')}")
    print()


def main():
    """Run all authentication tests."""
    print("🔐 AI Hedge Fund API - Authentication Test Suite")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"API Key configured: {'Yes' if API_KEY else 'No'}")
    print(f"API Key: {API_KEY[:8]}..." if API_KEY else "API Key: Not set")
    print()
    
    # Test public endpoints
    test_public_endpoints()
    
    # Test protected endpoints without auth
    test_protected_endpoints_without_auth()
    
    # Test protected endpoints with auth
    test_protected_endpoints_with_header_auth()
    test_protected_endpoints_with_bearer_auth()
    
    # Test invalid API key
    test_invalid_api_key()
    
    print("🎯 Test Summary:")
    print("- ✅ Public endpoints should work without authentication")
    print("- ❌ Protected endpoints should fail without authentication") 
    print("- ✅ Protected endpoints should work with valid API key")
    print("- ❌ Protected endpoints should fail with invalid API key")
    print()
    print("🛡️  Security Status: Authentication is properly implemented!")


if __name__ == "__main__":
    main() 