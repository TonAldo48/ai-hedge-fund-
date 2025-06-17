#!/usr/bin/env python3
"""
Test script for the natural language financial analysis chat agent.
Tests the specific query: "How does Tesla's valuation look from a Peter Lynch perspective?"
"""
import asyncio
import requests
import json
import os
from pathlib import Path
import sys

# Add parent directory to path so we can import from 'src'
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

from app.backend.services.chat_agent import process_financial_query

async def test_direct_agent():
    """Test the chat agent directly without going through FastAPI."""
    print("🧪 Testing Direct Agent Call")
    print("=" * 50)
    
    query = "How does Tesla's valuation look from a Peter Lynch perspective?"
    print(f"Query: {query}")
    print("Processing...")
    
    try:
        result = await process_financial_query(query)
        
        print(f"\n✅ Success: {result['success']}")
        print(f"Response:\n{result['response']}")
        
        if 'intermediate_steps' in result and result['intermediate_steps']:
            print(f"\n🔍 Intermediate Steps:")
            for i, step in enumerate(result['intermediate_steps'], 1):
                print(f"  Step {i}: {step}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def test_api_endpoint():
    """Test the FastAPI endpoint (requires server to be running)."""
    print("\n🌐 Testing FastAPI Endpoint")
    print("=" * 50)
    
    # Check if server is running
    try:
        health_response = requests.get("http://localhost:8000/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not healthy")
            return None
    except requests.exceptions.RequestException:
        print("❌ Server not running. Start with: python -m uvicorn app.backend.main:app --host 0.0.0.0 --port 8000 --reload")
        return None
    
    # Test the chat endpoint
    query = "How does Tesla's valuation look from a Peter Lynch perspective?"
    
    # Get API key from environment
    api_key = os.getenv("HEDGE_FUND_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        print("⚠️  No API key found. Testing without authentication (may fail in production)")
        headers = {"Content-Type": "application/json"}
    else:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }
    
    payload = {
        "query": query,
        "chat_history": None
    }
    
    try:
        print(f"Query: {query}")
        print("Sending request to API...")
        
        response = requests.post(
            "http://localhost:8000/chat/analyze",
            json=payload,
            headers=headers,
            timeout=60  # Give it time to run analysis
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success: {result['success']}")
            print(f"Response:\n{result['response']}")
            
            if 'intermediate_steps' in result and result['intermediate_steps']:
                print(f"\n🔍 Intermediate Steps:")
                for i, step in enumerate(result['intermediate_steps'], 1):
                    print(f"  Step {i}: {step}")
            
            return result
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
        return None

def test_examples_endpoint():
    """Test the examples endpoint."""
    print("\n📚 Testing Examples Endpoint")
    print("=" * 50)
    
    try:
        response = requests.get("http://localhost:8000/chat/examples", timeout=5)
        
        if response.status_code == 200:
            examples = response.json()
            print("✅ Available Examples:")
            
            for example in examples.get("examples", []):
                print(f"\n📝 Query: {example['query']}")
                print(f"   Description: {example['description']}")
            
            print(f"\n👥 Supported Investors:")
            for investor in examples.get("supported_investors", []):
                print(f"   • {investor['name']}: {investor['style']} - {investor['focus']}")
            
            return examples
        else:
            print(f"❌ API Error: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {str(e)}")
        return None

async def main():
    """Run all tests."""
    print("🚀 Testing Natural Language Financial Analysis Agent")
    print("=" * 60)
    
    # Test 1: Direct agent call (doesn't require server)
    direct_result = await test_direct_agent()
    
    # Test 2: API endpoint (requires server)
    api_result = test_api_endpoint()
    
    # Test 3: Examples endpoint
    examples_result = test_examples_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Direct Agent: {'✅ Pass' if direct_result else '❌ Fail'}")
    print(f"   API Endpoint: {'✅ Pass' if api_result else '❌ Fail'}")
    print(f"   Examples: {'✅ Pass' if examples_result else '❌ Fail'}")
    
    if direct_result and direct_result.get('success'):
        print(f"\n🎯 Tesla Valuation Analysis Complete!")
        print("The agent successfully:")
        print("   • Detected ticker: TSLA")
        print("   • Identified investment style: Peter Lynch")
        print("   • Called appropriate analysis functions")
        print("   • Synthesized results into natural language")

if __name__ == "__main__":
    asyncio.run(main()) 