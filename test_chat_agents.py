#!/usr/bin/env python3
"""
Test script for AI Hedge Fund Chat Agents
Tests the chat functionality of all implemented agents
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw"

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Test questions for different agent types
TEST_QUESTIONS = {
    "warren-buffett": "What are your thoughts on value investing in today's market?",
    "peter-lynch": "How do you identify growth stocks with potential?",
    "charlie-munger": "What mental models do you use for investment decisions?",
    "ben-graham": "How do you calculate intrinsic value for a stock?",
    "technical-analyst": "What technical indicators suggest a bullish trend?"
}

# Agent information
AGENTS = [
    {"id": "warren-buffett", "name": "Warren Buffett", "type": "value"},
    {"id": "peter-lynch", "name": "Peter Lynch", "type": "growth"},
    {"id": "charlie-munger", "name": "Charlie Munger", "type": "value"},
    {"id": "ben-graham", "name": "Ben Graham", "type": "value"},
    {"id": "technical-analyst", "name": "Technical Analyst", "type": "technical"}
]

def test_health_check():
    """Test if the API is running"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", headers=HEADERS)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_agent_chat(agent_id: str, question: str):
    """Test chat functionality for a specific agent"""
    print(f"\n🤖 Testing {agent_id} agent...")
    print(f"📝 Question: {question}")
    
    payload = {
        "message": question,
        "conversation_id": f"test-{agent_id}-{int(time.time())}"
    }
    
    try:
        # Start timer
        start_time = time.time()
        
        # Make request
        response = requests.post(
            f"{API_BASE_URL}/api/agents/{agent_id}/chat",
            headers=HEADERS,
            json=payload
        )
        
        # Calculate response time
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! (Response time: {response_time:.2f}s)")
            print(f"💬 Response: {data.get('response', 'No response')[:200]}...")
            
            # Check for metadata
            if 'metadata' in data:
                print(f"📊 Metadata: {json.dumps(data['metadata'], indent=2)}")
            
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_streaming_chat(agent_id: str, question: str):
    """Test streaming chat functionality"""
    print(f"\n🌊 Testing streaming for {agent_id} agent...")
    print(f"📝 Question: {question}")
    
    payload = {
        "message": question,
        "conversation_id": f"test-stream-{agent_id}-{int(time.time())}",
        "stream": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/agents/{agent_id}/chat",
            headers=HEADERS,
            json=payload,
            stream=True
        )
        
        if response.status_code == 200:
            print("✅ Streaming response:")
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    try:
                        # Parse SSE data
                        if line.startswith(b'data: '):
                            data = json.loads(line[6:])
                            if 'token' in data:
                                token = data['token']
                                print(token, end='', flush=True)
                                full_response += token
                    except:
                        pass
            
            print(f"\n📏 Total response length: {len(full_response)} characters")
            return True
        else:
            print(f"❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AI Hedge Fund Chat Agents Test Suite")
    print("=" * 50)
    
    # Check if API is running
    if not test_health_check():
        print("\n⚠️  API is not running. Please start the API server first.")
        print("Run: cd app/backend && python main.py")
        return
    
    print("\n" + "=" * 50)
    print("📋 Testing all chat agents...")
    print("=" * 50)
    
    results = []
    
    # Test each agent
    for agent in AGENTS:
        agent_id = agent['id']
        question = TEST_QUESTIONS.get(agent_id, "What is your investment philosophy?")
        
        # Test regular chat
        success = test_agent_chat(agent_id, question)
        results.append({
            "agent": agent['name'],
            "type": agent['type'],
            "regular_chat": "✅" if success else "❌"
        })
        
        # Small delay between requests
        time.sleep(1)
    
    # Test streaming for one agent
    print("\n" + "=" * 50)
    print("🌊 Testing streaming functionality...")
    print("=" * 50)
    
    streaming_success = test_streaming_chat(
        "warren-buffett", 
        "Explain your investment strategy in detail."
    )
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    
    print("\n| Agent | Type | Chat Status |")
    print("|-------|------|-------------|")
    for result in results:
        print(f"| {result['agent']:<15} | {result['type']:<10} | {result['regular_chat']} |")
    
    print(f"\nStreaming test: {'✅ Passed' if streaming_success else '❌ Failed'}")
    
    # Overall result
    all_passed = all(r['regular_chat'] == "✅" for r in results) and streaming_success
    print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed.'}")

if __name__ == "__main__":
    main() 