#!/usr/bin/env python3
"""
Test script to verify agent chat integration between frontend and backend
"""
import requests
import json
from datetime import datetime

API_KEY = "Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw"
BASE_URL = "http://localhost:8000"

def test_agent_chat(agent_name: str, query: str):
    """Test a specific agent's chat endpoint"""
    url = f"{BASE_URL}/api/agents/{agent_name}/analyze"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": query,
        "chat_history": []
    }
    
    print(f"\n{'='*60}")
    print(f"Testing {agent_name.replace('_', ' ').title()}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Success!")
        print(f"Response: {data['response'][:200]}...")
        print(f"Timestamp: {data['timestamp']}")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

def main():
    """Run tests for all agents"""
    print("🚀 Testing Agent Chat Integration")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test cases for each agent
    test_cases = [
        ("warren_buffett", "What's your view on Apple's competitive moat?"),
        ("peter_lynch", "Is Tesla still a growth stock?"),
        ("charlie_munger", "What mental models apply to investing in Microsoft?"),
        ("ben_graham", "Calculate the margin of safety for Google"),
        ("technical_analyst", "What do the charts say about Bitcoin?")
    ]
    
    for agent, query in test_cases:
        test_agent_chat(agent, query)

if __name__ == "__main__":
    main() 