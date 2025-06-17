#!/usr/bin/env python
"""
Test script for streaming Warren Buffett analysis.
This demonstrates real-time streaming of the agent's decision-making process.
"""

import asyncio
import json
import httpx
from datetime import datetime

async def test_streaming_analysis():
    """Test the streaming Warren Buffett analysis endpoint."""
    
    # Test query
    query = "What do you think about Tesla as a long-term investment?"
    
    print(f"🎯 Testing Streaming Warren Buffett Analysis")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    # Prepare request data
    request_data = {
        "query": query,
        "chat_history": []
    }
    
    # Stream the analysis
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            async with client.stream(
                "POST",
                "http://localhost:8000/warren-buffett/analyze-streaming",
                json=request_data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                    "X-API-Key": "test-key-12345"  # Use your API key
                }
            ) as response:
                
                if response.status_code != 200:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"Response: {await response.aread()}")
                    return
                
                print("🔄 Streaming Analysis Events:")
                print("-" * 40)
                
                async for line in response.aiter_lines():
                    if line.strip() and line.startswith("data: "):
                        # Parse the JSON data
                        data_str = line[6:]  # Remove "data: " prefix
                        try:
                            event = json.loads(data_str)
                            await display_event(event)
                        except json.JSONDecodeError:
                            print(f"📄 Raw data: {data_str}")
                        
                        # Small delay for readability
                        await asyncio.sleep(0.2)
                
        except Exception as e:
            print(f"❌ Error during streaming: {str(e)}")

async def display_event(event: dict):
    """Display streaming events in a user-friendly format."""
    
    event_type = event.get("type", "unknown")
    data = event.get("data", {})
    timestamp = event.get("timestamp", "")
    step = event.get("step", "")
    
    # Format timestamp
    time_str = ""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%H:%M:%S")
        except:
            time_str = timestamp
    
    if event_type == "start":
        print(f"🎯 [{time_str}] {data.get('message', 'Starting analysis...')}")
        print(f"   Query: {data.get('query', '')}")
        
    elif event_type == "agent_thinking":
        thought = data.get("thought", "")
        print(f"💭 [{time_str}] {thought}")
        
    elif event_type == "llm_thinking":
        print(f"🤔 [{time_str}] {data.get('message', 'AI is thinking...')}")
        if step:
            print(f"   Step: {step}")
            
    elif event_type == "llm_thought":
        thought = data.get("thought", "")
        print(f"💡 [{time_str}] Thought: {thought}")
        
    elif event_type == "agent_action":
        tool = data.get("tool", "")
        tool_input = data.get("tool_input", "")
        print(f"🔧 [{time_str}] Using tool: {tool}")
        print(f"   Input: {tool_input}")
        
    elif event_type == "tool_start":
        tool_name = data.get("tool_name", "")
        input_data = data.get("input", "")
        print(f"⚡ [{time_str}] Running {tool_name}...")
        print(f"   Analyzing: {input_data}")
        
    elif event_type == "tool_end":
        output = data.get("output", "")
        print(f"📊 [{time_str}] Analysis data received")
        if len(output) > 100:
            print(f"   Data: {output[:100]}...")
        else:
            print(f"   Data: {output}")
            
    elif event_type == "agent_finish":
        print(f"✅ [{time_str}] Analysis complete!")
        
    elif event_type == "complete":
        response = data.get("response", "")
        print(f"\n🎯 [{time_str}] FINAL RESPONSE:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        
    elif event_type == "error":
        error = data.get("error", "")
        print(f"❌ [{time_str}] Error: {error}")
        
    elif event_type == "heartbeat":
        print(f"💓 [{time_str}] {data.get('message', 'Processing...')}")
        
    elif event_type == "stream_end":
        print(f"\n🏁 [{time_str}] Stream completed")
        
    else:
        print(f"📄 [{time_str}] {event_type}: {data}")

async def test_direct_streaming():
    """Test streaming directly without HTTP (for development)."""
    print("🧪 Testing Direct Streaming (Development Mode)")
    print("=" * 50)
    
    try:
        from app.backend.services.warren_buffett_chat_agent import get_warren_buffett_agent
        
        agent = get_warren_buffett_agent()
        query = "How does Apple's moat look compared to its competitors?"
        
        print(f"Query: {query}\n")
        print("Streaming Events:")
        print("-" * 30)
        
        async for event_json in agent.analyze_streaming(query):
            event = json.loads(event_json)
            await display_event(event)
            await asyncio.sleep(0.1)  # Small delay for readability
            
    except Exception as e:
        print(f"❌ Direct streaming test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Warren Buffett Streaming Analysis Test")
    print("=" * 60)
    
    # Choose test mode
    print("1. Test via HTTP endpoint (requires server running)")
    print("2. Test direct streaming (development mode)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_streaming_analysis())
    elif choice == "2":
        asyncio.run(test_direct_streaming())
    else:
        print("Invalid choice. Running HTTP test by default.")
        asyncio.run(test_streaming_analysis()) 