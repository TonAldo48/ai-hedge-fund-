#!/usr/bin/env python3
"""
Test script for the backtesting API endpoints.
Shows how to start a backtest and stream real-time updates.
"""
import requests
import json
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="../../.env")

def get_api_key():
    """Get API key from environment variables."""
    return os.getenv("API_KEY") or os.getenv("HEDGE_FUND_API_KEY")

def test_backtest_streaming():
    """Test the streaming backtest endpoint."""
    print("🚀 Testing AI Hedge Fund Backtesting API...\n")
    
    base_url = "http://localhost:8000"
    api_key = get_api_key()
    headers = {
        "Content-Type": "application/json"
    }
    
    # Add API key if available
    if api_key:
        headers["X-API-Key"] = api_key
        print(f"🔑 Using API key: {api_key[:10]}...")
    else:
        print("⚠️ No API key found - running in development mode")
    
    # Calculate 2-week timeframe for faster testing
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=2)
    
    # Payload for backtest
    payload = {
        "tickers": ["AAPL", "MSFT"],
        "selected_agents": ["michael_burry", "cathie_wood"],
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "model_name": "gpt-4o-mini",
        "model_provider": "OpenAI",
        "initial_capital": 100000,
        "margin_requirement": 0.0,
        "show_reasoning": True
    }
    
    print(f"📤 Backtest Request: {json.dumps(payload, indent=2)}")
    print(f"🔗 Base URL: {base_url}\n")
    
    try:
        # Step 1: Start the backtest
        print("🔹 Step 1: Starting backtest...")
        start_response = requests.post(
            f"{base_url}/backtest/start",
            json=payload,
            headers=headers,
            timeout=30
        )
        
        if start_response.status_code != 200:
            print(f"❌ Failed to start backtest: {start_response.status_code}")
            print(f"Response: {start_response.text}")
            return
        
        start_data = start_response.json()
        backtest_id = start_data["backtest_id"]
        
        print(f"✅ Backtest started successfully!")
        print(f"📍 Backtest ID: {backtest_id}")
        print(f"🔗 Stream URL: {start_data['stream_url']}")
        print(f"📊 Status URL: {start_data['status_url']}\n")
        
        # Step 2: Stream the updates
        print("🔹 Step 2: Streaming backtest updates...")
        print("📡 Real-time events:\n")
        
        stream_headers = {
            **headers,
            "Accept": "text/event-stream"
        }
        
        with requests.get(
            f"{base_url}/backtest/stream/{backtest_id}",
            headers=stream_headers,
            stream=True,
            timeout=300  # 5 minute timeout
        ) as response:
            
            if response.status_code != 200:
                print(f"❌ Stream error: {response.status_code}")
                print(f"Response: {response.text}")
                return
            
            event_count = 0
            
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    event_count += 1
                    
                    # Parse SSE format
                    if line.startswith("event:"):
                        event_type = line.split(":", 1)[1].strip()
                        print(f"🔸 Event {event_count}: {event_type}")
                    
                    elif line.startswith("data:"):
                        data_str = line.split(":", 1)[1].strip()
                        try:
                            data = json.loads(data_str)
                            
                            event_type = data.get("type", "unknown")
                            
                            if event_type == "backtest_start":
                                print(f"   ✅ Backtest started - {data.get('total_days', 0)} trading days")
                                print(f"   📈 Tickers: {', '.join(data.get('tickers', []))}")
                                
                            elif event_type == "backtest_progress":
                                progress = data.get("progress", 0) * 100
                                current_date = data.get("current_date", "")
                                completed = data.get("completed_days", 0)
                                total = data.get("total_days", 0)
                                print(f"   📊 Progress: {progress:.1f}% ({completed}/{total}) - {current_date}")
                                
                            elif event_type == "trading":
                                ticker = data.get("ticker", "")
                                action = data.get("action", "").upper()
                                quantity = data.get("quantity", 0)
                                price = data.get("price", 0)
                                portfolio_value = data.get("portfolio_value", 0)
                                print(f"   💰 Trade: {action} {quantity} {ticker} @ ${price:.2f}")
                                print(f"       Portfolio Value: ${portfolio_value:,.2f}")
                                
                            elif event_type == "portfolio_update":
                                date = data.get("date", "")
                                total_value = data.get("total_value", 0)
                                daily_return = data.get("daily_return")
                                return_str = f"{daily_return*100:+.2f}%" if daily_return else "N/A"
                                print(f"   📈 Portfolio [{date}]: ${total_value:,.2f} (daily: {return_str})")
                                
                            elif event_type == "performance_update":
                                total_return = data.get("total_return", 0)
                                sharpe = data.get("sharpe_ratio")
                                max_dd = data.get("max_drawdown")
                                print(f"   📊 Performance Update:")
                                print(f"       Total Return: {total_return:+.2f}%")
                                if sharpe: print(f"       Sharpe Ratio: {sharpe:.2f}")
                                if max_dd: print(f"       Max Drawdown: {max_dd:.2f}%")
                                
                            elif event_type == "backtest_complete":
                                print(f"   🎯 Backtest Complete!")
                                final_perf = data.get("final_performance", {})
                                print(f"   💰 Final Results:")
                                print(f"       Total Return: {final_perf.get('total_return', 0):+.2f}%")
                                print(f"       Final Value: ${final_perf.get('final_value', 0):,.2f}")
                                print(f"       Initial Capital: ${final_perf.get('initial_capital', 0):,.2f}")
                                if final_perf.get('sharpe_ratio'): 
                                    print(f"       Sharpe Ratio: {final_perf.get('sharpe_ratio'):.2f}")
                                if final_perf.get('max_drawdown'): 
                                    print(f"       Max Drawdown: {final_perf.get('max_drawdown'):.2f}%")
                                break
                                
                            elif event_type == "keepalive":
                                pass  # Skip keepalive messages
                                
                            else:
                                print(f"   📄 {event_type}: {data}")
                                
                        except json.JSONDecodeError:
                            print(f"   📄 Raw data: {data_str}")
                    
                    print()  # Empty line for readability
        
        print(f"✅ Streaming complete! Processed {event_count} events.")
        
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")


def test_backtest_sync():
    """Test the synchronous backtest endpoint."""
    print("🚀 Testing Synchronous Backtest API...\n")
    
    base_url = "http://localhost:8000"
    api_key = get_api_key()
    headers = {
        "Content-Type": "application/json"
    }
    
    # Add API key if available
    if api_key:
        headers["X-API-Key"] = api_key
        print(f"🔑 Using API key: {api_key[:10]}...")
    else:
        print("⚠️ No API key found - running in development mode")
    
    # Calculate 1-week timeframe for faster testing
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=1)
    
    payload = {
        "tickers": ["AAPL"],
        "selected_agents": ["warren_buffett"],
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "model_name": "gpt-4o-mini",
        "model_provider": "OpenAI",
        "initial_capital": 50000,
        "margin_requirement": 0.0
    }
    
    print(f"📤 Request: {json.dumps(payload, indent=2)}")
    
    try:
        print("⏳ Running synchronous backtest (this may take a while)...")
        
        response = requests.post(
            f"{base_url}/backtest/run-sync",
            json=payload,
            headers=headers,
            timeout=300  # 5 minute timeout
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        result = response.json()
        
        print("✅ Backtest completed!")
        print(f"📊 Performance Metrics:")
        perf = result.get("performance_metrics", {})
        print(f"   Total Return: {perf.get('total_return', 0):+.2f}%")
        print(f"   Final Value: ${perf.get('final_value', 0):,.2f}")
        print(f"   Initial Capital: ${perf.get('initial_capital', 0):,.2f}")
        if perf.get('sharpe_ratio'): 
            print(f"   Sharpe Ratio: {perf.get('sharpe_ratio'):.2f}")
        if perf.get('max_drawdown'): 
            print(f"   Max Drawdown: {perf.get('max_drawdown'):.2f}%")
        
        history = result.get("portfolio_history", [])
        print(f"\n📈 Portfolio History ({len(history)} data points)")
        if history:
            print(f"   Start: {history[0]['date']} - ${history[0]['value']:,.2f}")
            print(f"   End: {history[-1]['date']} - ${history[-1]['value']:,.2f}")
        
    except requests.exceptions.Timeout:
        print("⏱️ Request timed out")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        test_backtest_sync()
    else:
        test_backtest_streaming()
        
    print("\n" + "="*60)
    print("💡 Usage:")
    print("   python test_backtest_api.py        # Test streaming API")
    print("   python test_backtest_api.py sync   # Test synchronous API") 