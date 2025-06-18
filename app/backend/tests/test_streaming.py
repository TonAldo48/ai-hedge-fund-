#!/usr/bin/env python3
"""
Test script for the streaming hedge fund API endpoint.
Shows real-time progress updates as AI agents analyze stocks.
"""
import requests
import json
import time
from datetime import datetime, timedelta

def test_streaming_endpoint():
    """Test the streaming endpoint with Server-Sent Events."""
    print("🚀 Testing AI Hedge Fund Streaming API...\n")
    
    url = "https://aeeroooo-production.up.railway.app/hedge-fund/run"
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    # Calculate 10-day timeframe
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10)
    
    # Payload with 10-day timeframe and multiple agents
    payload = {
        "tickers": ["AAPL", "MSFT", "NVDA"],
        "selected_agents": ["warren_buffett", "technical_analyst"],
        "model_name": "gpt-4o-mini",
        "model_provider": "OpenAI",
        "initial_cash": 50000,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "show_reasoning": True
    }
    
    print(f"📤 Request: {json.dumps(payload, indent=2)}")
    print(f"🔗 URL: {url}\n")
    print("📡 Streaming events:\n")
    
    try:
        # Make the streaming request
        with requests.post(url, json=payload, headers=headers, stream=True, timeout=120) as response:
            if response.status_code != 200:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                return
            
            # Process streaming events
            event_count = 0
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    event_count += 1
                    
                    # Parse SSE format
                    if line.startswith("event:"):
                        event_type = line.split(":", 1)[1].strip()
                        print(f"🔹 Event {event_count}: {event_type}")
                    
                    elif line.startswith("data:"):
                        data_str = line.split(":", 1)[1].strip()
                        try:
                            data = json.loads(data_str)
                            
                            # Pretty print based on event type
                            if data.get("type") == "start":
                                print("   ✅ Analysis started")
                                
                            elif data.get("type") == "progress":
                                agent = data.get("agent", "Unknown")
                                ticker = data.get("ticker", "")
                                status = data.get("status", "")
                                timestamp = data.get("timestamp", "")
                                print(f"   📊 {agent} analyzing {ticker}: {status}")
                                print(f"   ⏰ {timestamp}")
                                
                            elif data.get("type") == "complete":
                                print("   🎯 Analysis complete!")
                                decisions = data.get("data", {}).get("decisions", {})
                                for ticker, decision in decisions.items():
                                    action = decision.get("action", "N/A")
                                    quantity = decision.get("quantity", 0)
                                    confidence = decision.get("confidence", 0)
                                    reasoning = decision.get("reasoning", "")
                                    print(f"   📈 {ticker}: {action.upper()} {quantity} shares ({confidence}% confidence)")
                                    print(f"   💭 Reasoning: {reasoning[:100]}...")
                                
                            else:
                                print(f"   📄 Data: {data}")
                                
                        except json.JSONDecodeError:
                            print(f"   📄 Raw data: {data_str}")
                    
                    print()  # Empty line for readability
                    
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out after 120 seconds")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    
    print(f"\n✅ Streaming test complete! Processed {event_count} events.")

if __name__ == "__main__":
    test_streaming_endpoint() 



