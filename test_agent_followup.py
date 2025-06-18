#!/usr/bin/env python3
"""
Test follow-up questions in agent chat to ensure chat history is properly maintained
"""
import requests
import json
from datetime import datetime
import time

API_KEY = "Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw"
BASE_URL = "http://localhost:8000"

def test_followup_conversation(agent_name: str, questions: list):
    """Test a conversation with follow-up questions"""
    url = f"{BASE_URL}/api/agents/{agent_name}/analyze"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    chat_history = []
    
    print(f"\n{'='*60}")
    print(f"Testing Follow-up Conversation with {agent_name.replace('_', ' ').title()}")
    print(f"{'='*60}\n")
    
    for i, question in enumerate(questions):
        print(f"Question {i+1}: {question}")
        
        payload = {
            "message": question,
            "chat_history": chat_history
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            answer = data['response']
            
            print(f"Answer: {answer[:200]}...\n")
            
            # Add to chat history
            chat_history.append({
                "role": "user",
                "content": question
            })
            chat_history.append({
                "role": "assistant", 
                "content": answer
            })
            
            # Small delay between questions
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            break

def main():
    """Run follow-up conversation tests"""
    print("🚀 Testing Agent Chat Follow-up Questions")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test Warren Buffett with follow-ups
    warren_questions = [
        "What's your view on Apple's competitive moat?",
        "How does that compare to Microsoft's moat?",
        "Which one would you prefer for a long-term investment?"
    ]
    test_followup_conversation("warren_buffett", warren_questions)
    
    # Test Peter Lynch with follow-ups
    lynch_questions = [
        "What's Tesla's PEG ratio?",
        "Is that considered high or low?",
        "What other growth stocks have better PEG ratios?"
    ]
    test_followup_conversation("peter_lynch", lynch_questions)
    
    # Test Technical Analyst with follow-ups
    technical_questions = [
        "What's the current trend for Bitcoin?",
        "Where are the key support levels?",
        "Should I wait for a pullback before buying?"
    ]
    test_followup_conversation("technical_analyst", technical_questions)

if __name__ == "__main__":
    main() 