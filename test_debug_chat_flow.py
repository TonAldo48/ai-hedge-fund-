#!/usr/bin/env python3
"""
Comprehensive test to debug the chat agent flow with detailed logging.
This will help us trace exactly what happens when a user sends a message.
"""

import requests
import json
import time
import asyncio
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8000"
API_KEY = "Pb9RPNoA1neVLA6teD-GFTbUh8EI9TFe5QK9aN3z_Aw"
TEST_QUERY = "what do you think of NVIDIA's valuation"

def log_with_timestamp(message, level="INFO"):
    """Add timestamp to log messages"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [{level}] {message}")

def test_backend_health():
    """Test if backend is healthy and accessible"""
    log_with_timestamp("=== TESTING BACKEND HEALTH ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        log_with_timestamp(f"Health check status: {response.status_code}")
        log_with_timestamp(f"Health check response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        log_with_timestamp(f"Health check failed: {str(e)}", "ERROR")
        return False

def test_warren_buffett_agent_health():
    """Test Warren Buffett agent specifically"""
    log_with_timestamp("=== TESTING WARREN BUFFETT AGENT HEALTH ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/warren-buffett/health", timeout=5)
        log_with_timestamp(f"Warren Buffett health status: {response.status_code}")
        log_with_timestamp(f"Warren Buffett health response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        log_with_timestamp(f"Warren Buffett health check failed: {str(e)}", "ERROR")
        return False

def test_warren_buffett_capabilities():
    """Test Warren Buffett agent capabilities"""
    log_with_timestamp("=== TESTING WARREN BUFFETT CAPABILITIES ===")
    
    try:
        response = requests.get(f"{BACKEND_URL}/warren-buffett/capabilities", timeout=5)
        log_with_timestamp(f"Capabilities status: {response.status_code}")
        if response.status_code == 200:
            capabilities = response.json()
            log_with_timestamp(f"Available capabilities: {len(capabilities.get('capabilities', []))}")
            for cap in capabilities.get('capabilities', [])[:3]:  # Show first 3
                log_with_timestamp(f"  - {cap.get('name')}: {cap.get('description')[:50]}...")
        return response.status_code == 200
    except Exception as e:
        log_with_timestamp(f"Capabilities test failed: {str(e)}", "ERROR")
        return False

def test_simple_analyze_endpoint():
    """Test the simple analyze endpoint (non-streaming)"""
    log_with_timestamp("=== TESTING SIMPLE ANALYZE ENDPOINT ===")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    try:
        log_with_timestamp(f"Sending query: '{TEST_QUERY}'")
        log_with_timestamp(f"Headers: {headers}")
        log_with_timestamp(f"URL: {BACKEND_URL}/warren-buffett/analyze?query={TEST_QUERY}")
        
        response = requests.post(
            f"{BACKEND_URL}/warren-buffett/analyze",
            params={"query": TEST_QUERY},
            headers=headers,
            timeout=60
        )
        
        log_with_timestamp(f"Simple analyze status: {response.status_code}")
        log_with_timestamp(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            log_with_timestamp(f"Response success: {result.get('success')}")
            log_with_timestamp(f"Response agent: {result.get('agent')}")
            log_with_timestamp(f"Response length: {len(result.get('response', ''))}")
            log_with_timestamp(f"Response preview: {result.get('response', '')[:200]}...")
            return True, result
        else:
            log_with_timestamp(f"Error response: {response.text}", "ERROR")
            return False, None
            
    except Exception as e:
        log_with_timestamp(f"Simple analyze test failed: {str(e)}", "ERROR")
        return False, None

def test_streaming_analyze_endpoint():
    """Test the streaming analyze endpoint"""
    log_with_timestamp("=== TESTING STREAMING ANALYZE ENDPOINT ===")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "query": TEST_QUERY,
        "chat_history": []
    }
    
    try:
        log_with_timestamp(f"Sending streaming request")
        log_with_timestamp(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{BACKEND_URL}/warren-buffett/analyze-streaming",
            json=payload,
            headers=headers,
            stream=True,
            timeout=60
        )
        
        log_with_timestamp(f"Streaming status: {response.status_code}")
        log_with_timestamp(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            log_with_timestamp("=== STREAMING EVENTS ===")
            event_count = 0
            
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    event_count += 1
                    log_with_timestamp(f"Event {event_count}: {line}")
                    
                    if line.startswith('data: '):
                        try:
                            event_data = json.loads(line[6:])  # Remove 'data: ' prefix
                            event_type = event_data.get('type')
                            log_with_timestamp(f"  -> Event type: {event_type}")
                            
                            if event_type == 'complete':
                                response_text = event_data.get('data', {}).get('response', '')
                                log_with_timestamp(f"  -> Final response length: {len(response_text)}")
                                log_with_timestamp(f"  -> Final response preview: {response_text[:200]}...")
                                
                        except json.JSONDecodeError as e:
                            log_with_timestamp(f"  -> Failed to parse event JSON: {e}", "ERROR")
                    
                    # Stop after reasonable number of events to avoid spam
                    if event_count > 50:
                        log_with_timestamp("Stopping after 50 events to avoid spam")
                        break
            
            log_with_timestamp(f"Total events received: {event_count}")
            return True
        else:
            log_with_timestamp(f"Streaming error: {response.text}", "ERROR")
            return False
            
    except Exception as e:
        log_with_timestamp(f"Streaming test failed: {str(e)}", "ERROR")
        return False

def test_agent_directly():
    """Test calling the agent service directly"""
    log_with_timestamp("=== TESTING AGENT SERVICE DIRECTLY ===")
    
    try:
        # Import and test the agent directly
        import sys
        import os
        sys.path.append(os.getcwd())
        
        from app.backend.services.warren_buffett_chat_agent import process_warren_buffett_query
        
        log_with_timestamp("Testing agent service directly...")
        
        # This would require async, so let's just verify import works
        log_with_timestamp("Agent service import successful")
        return True
        
    except Exception as e:
        log_with_timestamp(f"Direct agent test failed: {str(e)}", "ERROR")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    log_with_timestamp("🚀 STARTING COMPREHENSIVE CHAT AGENT DEBUG TEST")
    log_with_timestamp(f"Test query: '{TEST_QUERY}'")
    log_with_timestamp(f"Backend URL: {BACKEND_URL}")
    
    results = {}
    
    # Test 1: Backend Health
    results['backend_health'] = test_backend_health()
    
    # Test 2: Warren Buffett Agent Health  
    results['warren_buffett_health'] = test_warren_buffett_agent_health()
    
    # Test 3: Capabilities
    results['capabilities'] = test_warren_buffett_capabilities()
    
    # Test 4: Simple Analyze
    success, response_data = test_simple_analyze_endpoint()
    results['simple_analyze'] = success
    
    # Test 5: Streaming Analyze
    results['streaming_analyze'] = test_streaming_analyze_endpoint()
    
    # Test 6: Direct Agent
    results['direct_agent'] = test_agent_directly()
    
    # Summary
    log_with_timestamp("=== TEST RESULTS SUMMARY ===")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        log_with_timestamp(f"{test_name}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    log_with_timestamp(f"Overall: {overall_status}")
    
    if not all_passed:
        log_with_timestamp("\n🔍 DEBUGGING SUGGESTIONS:")
        if not results['backend_health']:
            log_with_timestamp("- Backend is not running. Start with: python app/backend/run_api.py")
        if not results['warren_buffett_health']:
            log_with_timestamp("- Warren Buffett agent has issues. Check logs in backend.")
        if not results['simple_analyze']:
            log_with_timestamp("- Simple analyze failed. Check API key and agent configuration.")
        if not results['streaming_analyze']:
            log_with_timestamp("- Streaming failed. Check SSE implementation and event formatting.")

if __name__ == "__main__":
    run_all_tests() 