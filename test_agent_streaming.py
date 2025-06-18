"""
Test script to verify agent streaming functionality
"""
import asyncio
import aiohttp
import json
from datetime import datetime

API_KEY = "Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw"
BASE_URL = "http://localhost:8000"

async def test_agent_streaming(agent_name: str, query: str):
    """Test streaming response from a specific agent."""
    print(f"\n🧪 Testing {agent_name} streaming...")
    print(f"📝 Query: {query}")
    print("-" * 50)
    
    url = f"{BASE_URL}/api/agents/{agent_name}/analyze-streaming"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream"
    }
    
    payload = {
        "message": query,
        "chat_history": []
    }
    
    start_time = datetime.now()
    events_received = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ Error: {response.status} - {error_text}")
                    return
                
                print("✅ Connected to stream")
                
                # Read the stream
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    
                    if not line_str:
                        continue
                        
                    if line_str.startswith("data: "):
                        data = line_str[6:]
                        
                        if data == "[DONE]":
                            print("\n✅ Stream completed")
                            break
                            
                        try:
                            event = json.loads(data)
                            events_received.append(event)
                            
                            # Display different event types
                            event_type = event.get("type", "unknown")
                            
                            if event_type == "message-start":
                                print(f"🚀 Message started (ID: {event.get('id', 'N/A')[:8]}...)")
                            elif event_type == "text-delta":
                                print(event.get("textDelta", ""), end="", flush=True)
                            elif event_type == "message-end":
                                print(f"\n✅ Message ended")
                            elif event_type == "error":
                                print(f"\n❌ Error: {event.get('error', 'Unknown error')}")
                            else:
                                print(f"\n📊 Event: {event_type}")
                                
                        except json.JSONDecodeError as e:
                            print(f"\n⚠️  Could not parse: {data[:50]}...")
                
                elapsed = (datetime.now() - start_time).total_seconds()
                print(f"\n⏱️  Total time: {elapsed:.2f}s")
                print(f"📊 Events received: {len(events_received)}")
                
                # Show event type breakdown
                event_types = {}
                for event in events_received:
                    event_type = event.get("type", "unknown")
                    event_types[event_type] = event_types.get(event_type, 0) + 1
                
                print("\n📈 Event breakdown:")
                for event_type, count in event_types.items():
                    print(f"  - {event_type}: {count}")
                    
    except Exception as e:
        print(f"\n❌ Exception: {type(e).__name__}: {e}")


async def test_non_streaming(agent_name: str, query: str):
    """Test non-streaming response for comparison."""
    print(f"\n🧪 Testing {agent_name} non-streaming...")
    
    url = f"{BASE_URL}/api/agents/{agent_name}/analyze"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": query,
        "chat_history": []
    }
    
    start_time = datetime.now()
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ Error: {response.status} - {error_text}")
                    return
                
                data = await response.json()
                elapsed = (datetime.now() - start_time).total_seconds()
                
                print(f"✅ Response received in {elapsed:.2f}s")
                print(f"📝 Response: {data.get('response', 'No response')[:200]}...")
                
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")


async def main():
    """Run streaming tests for different agents."""
    test_cases = [
        ("warren_buffett", "What's your analysis of Apple stock?"),
        ("peter_lynch", "Is Tesla a good growth stock to buy now?"),
        ("technical_analyst", "What do the charts say about Bitcoin?"),
        ("charlie_munger", "What mental models apply to Amazon's business?"),
        ("ben_graham", "Calculate the margin of safety for Microsoft")
    ]
    
    print("🚀 AI Hedge Fund Agent Streaming Test")
    print("=" * 50)
    
    # Test streaming for each agent
    for agent_name, query in test_cases:
        await test_agent_streaming(agent_name, query)
        await asyncio.sleep(1)  # Small delay between tests
    
    print("\n\n📊 Comparing with non-streaming...")
    print("=" * 50)
    
    # Compare with non-streaming
    agent_name, query = test_cases[0]
    await test_non_streaming(agent_name, query)


if __name__ == "__main__":
    asyncio.run(main()) 