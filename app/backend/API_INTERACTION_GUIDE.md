# AI Hedge Fund API - Interactive Guide

## Overview

This guide documents real interactions with the AI Hedge Fund API, showing the complete journey from CLI to web API with actual requests, responses, and streaming examples.

## 🚀 Getting Started

### 1. Starting the API Server

```bash
# Start the API server
poetry run python app/backend/run_api.py

# Server runs at: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### 2. Basic Health Check

**Request:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-05-29T05:28:28.974380Z",
  "service": "AI Hedge Fund API"
}
```

---

## 📝 API Endpoints Overview

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/hedge-fund/agents` | GET | List available AI agents |
| `/hedge-fund/models` | GET | List available LLM models |
| `/hedge-fund/run-sync` | POST | Synchronous analysis |
| `/hedge-fund/run` | POST | Streaming analysis |

---

## 🤖 Available AI Agents

**Request:**
```bash
curl http://localhost:8000/hedge-fund/agents
```

**Response:**
```json
{
  "agents": [
    {"id": "aswath_damodaran", "name": "Aswath Damodaran"},
    {"id": "ben_graham", "name": "Ben Graham"},
    {"id": "bill_ackman", "name": "Bill Ackman"},
    {"id": "cathie_wood", "name": "Cathie Wood"},
    {"id": "charlie_munger", "name": "Charlie Munger"},
    {"id": "michael_burry", "name": "Michael Burry"},
    {"id": "peter_lynch", "name": "Peter Lynch"},
    {"id": "phil_fisher", "name": "Phil Fisher"},
    {"id": "stanley_druckenmiller", "name": "Stanley Druckenmiller"},
    {"id": "warren_buffett", "name": "Warren Buffett"},
    {"id": "technical_analyst", "name": "Technical Analyst"},
    {"id": "fundamentals_analyst", "name": "Fundamentals Analyst"},
    {"id": "sentiment_analyst", "name": "Sentiment Analyst"},
    {"id": "valuation_analyst", "name": "Valuation Analyst"}
  ]
}
```

---

## 🔧 Available Models

**Request:**
```bash
curl http://localhost:8000/hedge-fund/models
```

**Response (truncated):**
```json
{
  "models": [
    {
      "display_name": "[openai] gpt 4o",
      "model_name": "gpt-4o",
      "provider": "OpenAI"
    },
    {
      "display_name": "[anthropic] claude haiku 3.5",
      "model_name": "claude-3-5-haiku-latest",
      "provider": "Anthropic"
    },
    {
      "display_name": "[deepseek] deepseek v3",
      "model_name": "deepseek-chat",
      "provider": "DeepSeek"
    }
  ]
}
```

---

## 📊 Synchronous Analysis Examples

### Example 1: Simple Single-Agent Analysis

**Request:**
```bash
curl -X POST "http://localhost:8000/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["technical_analyst"],
    "model_name": "gpt-4o",
    "model_provider": "OpenAI",
    "initial_cash": 50000
  }'
```

**Response:**
```json
{
  "decisions": {
    "AAPL": {
      "action": "hold",
      "quantity": 0,
      "confidence": 15.0,
      "reasoning": "The technical analysis signal is neutral with low confidence, indicating no clear direction. Therefore, holding the current position is the prudent action as there is no compelling reason to buy or sell."
    }
  },
  "analyst_signals": {
    "technical_analyst_agent": {
      "AAPL": {
        "signal": "neutral",
        "confidence": 15,
        "strategy_signals": {
          "trend_following": {
            "signal": "bearish",
            "confidence": 26,
            "metrics": {
              "adx": 26.247869496501956,
              "trend_strength": 0.2624786949650196
            }
          },
          "mean_reversion": {
            "signal": "neutral",
            "confidence": 50,
            "metrics": {
              "z_score": -0.4913226464895977,
              "price_vs_bb": 0.33264158186003220,
              "rsi_14": 55.27981767536083,
              "rsi_28": 53.69369369369368
            }
          }
        }
      }
    }
  },
  "metadata": {
    "tickers": ["AAPL"],
    "start_date": "2025-02-27",
    "end_date": "2025-05-28",
    "model": "OpenAI:gpt-4o",
    "selected_agents": ["technical_analyst"]
  }
}
```

### Example 2: Multi-Agent Analysis

**Request:**
```bash
curl -X POST "http://localhost:8000/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "selected_agents": ["warren_buffett", "technical_analyst", "peter_lynch"],
    "model_name": "gpt-4o",
    "model_provider": "OpenAI",
    "initial_cash": 100000,
    "start_date": "2024-01-01",
    "end_date": "2024-01-15"
  }'
```

**Response (Key Highlights):**
```json
{
  "decisions": {
    "AAPL": {
      "action": "short",
      "quantity": 107,
      "confidence": 85.0,
      "reasoning": "Warren Buffett agent gave a strong bearish signal with high confidence, and there are no long or short positions in AAPL. Shorting 107 shares as it's the maximum allowed."
    },
    "MSFT": {
      "action": "buy",
      "quantity": 51,
      "confidence": 90.0,
      "reasoning": "Peter Lynch agent provided a bullish signal with high confidence. Buying the maximum of 51 shares, respecting portfolio cash and maximum shares allowed."
    },
    "GOOGL": {
      "action": "buy",
      "quantity": 140,
      "confidence": 85.0,
      "reasoning": "Both technical and Peter Lynch agents gave bullish signals with high confidence. Buying the maximum of 140 shares respecting portfolio cash and maximum shares allowed."
    }
  },
  "analyst_signals": {
    "warren_buffett_agent": {
      "AAPL": {
        "signal": "bearish",
        "confidence": 85.0,
        "reasoning": "Looking at Apple's financials reminds me a bit of a dazzling but strained performer on Wall Street... Apple's current debt to equity ratio standing at 3.8 is concerningly high... The price multiples, such as a PE ratio nearing 30 and the price to book at over 40, indicate that the stock trades at a premium..."
      }
    },
    "peter_lynch_agent": {
      "MSFT": {
        "signal": "bullish",
        "confidence": 90.0,
        "reasoning": "Now here's a company I can get behind! Microsoft is just one of those businesses that's everywhere you look... PEG ratio of 0.39 - that's telling us you're getting growth at a very reasonable price..."
      }
    }
  }
}
```

### Example 3: With Detailed Reasoning (New!)

**Request:**
```bash
curl -X POST "http://localhost:8000/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["warren_buffett"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI",
    "initial_cash": 50000,
    "show_reasoning": true
  }'
```

**Response with Enhanced Reasoning:**
```json
{
  "decisions": {
    "AAPL": {
      "action": "hold",
      "quantity": 0,
      "confidence": 75.0,
      "reasoning": "Warren Buffett analysis shows mixed signals. While Apple has strong fundamentals and competitive moats, the current valuation appears stretched. The show_reasoning flag provides detailed step-by-step analysis in the analyst_signals section."
    }
  },
  "analyst_signals": {
    "warren_buffett_agent": {
      "AAPL": {
        "signal": "neutral",
        "confidence": 75.0,
        "reasoning": "**Detailed Warren Buffett Analysis:**\n\n1. **Business Quality**: Apple operates in a highly competitive but profitable sector...\n2. **Competitive Moat**: Strong brand loyalty and ecosystem lock-in...\n3. **Management Quality**: Tim Cook has proven capable leadership...\n4. **Financial Metrics**: Strong balance sheet but high debt-to-equity...\n5. **Valuation**: Current P/E of 29x is above my typical comfort zone...\n6. **Long-term Prospects**: Continued innovation in services and AR/VR..."
      }
    }
  }
}
```

---

## 🌊 Streaming Analysis Examples

### Example 1: Basic Streaming

**Request:**
```bash
curl -X POST "http://localhost:8000/hedge-fund/run" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["technical_analyst"],
    "model_name": "gpt-4o",
    "model_provider": "OpenAI",
    "initial_cash": 50000,
    "start_date": "2025-05-18",
    "end_date": "2025-05-28"
  }' \
  --no-buffer
```

**Streaming Response:**
```
event: start
data: {"type":"start","timestamp":null}

event: progress
data: {"type":"progress","agent":"technical_analyst_agent","ticker":"AAPL","status":"Analyzing price data","timestamp":"2025-05-29T06:02:21.736414+00:00","analysis":null}

event: progress
data: {"type":"progress","agent":"technical_analyst_agent","ticker":"AAPL","status":"Calculating trend signals","timestamp":"2025-05-29T06:02:22.440291+00:00","analysis":null}

event: progress
data: {"type":"progress","agent":"technical_analyst_agent","ticker":"AAPL","status":"Calculating mean reversion","timestamp":"2025-05-29T06:02:22.448004+00:00","analysis":null}

event: progress
data: {"type":"progress","agent":"technical_analyst_agent","ticker":"AAPL","status":"Calculating momentum","timestamp":"2025-05-29T06:02:22.450395+00:00","analysis":null}

event: progress
data: {"type":"progress","agent":"technical_analyst_agent","ticker":"AAPL","status":"Analyzing volatility","timestamp":"2025-05-29T06:02:22.451420+00:00","analysis":null}

event: progress
data: {"type":"progress","agent":"technical_analyst_agent","ticker":"AAPL","status":"Statistical analysis","timestamp":"2025-05-29T06:02:22.452524+00:00","analysis":null}

event: progress
data: {"type":"progress","agent":"technical_analyst_agent","ticker":"AAPL","status":"Combining signals","timestamp":"2025-05-29T06:02:22.454974+00:00","analysis":null}

event: progress
data: {"type":"progress","agent":"technical_analyst_agent","ticker":"AAPL","status":"Done","timestamp":"2025-05-29T06:02:22.455076+00:00","analysis":null}

event: progress
data: {"type":"progress","agent":"risk_management_agent","ticker":"AAPL","status":"Current price: 200.21","timestamp":"2025-05-29T06:02:22.456603+00:00","analysis":null}

event: progress
data: {"type":"progress","agent":"portfolio_manager","ticker":"AAPL","status":"Processing analyst signals","timestamp":"2025-05-29T06:02:22.456974+00:00","analysis":null}

event: complete
data: {"type":"complete","data":{"decisions":{"AAPL":{"action":"hold","quantity":0,"confidence":32.0,"reasoning":"The analysis by the technical analyst agent suggests a bearish sentiment on AAPL with a confidence level of 32%..."}}}}
```

### Example 2: Enhanced Multi-Agent Streaming

**Python Test Script:**
```python
import requests
import json
from datetime import datetime, timedelta

# Setup
url = "http://localhost:8000/hedge-fund/run"
headers = {
    "Content-Type": "application/json",
    "Accept": "text/event-stream"
}

# Calculate timeframe
end_date = datetime.now()
start_date = end_date - timedelta(days=10)

# Enhanced payload
payload = {
    "tickers": ["AAPL", "MSFT", "NVDA"],
    "selected_agents": ["warren_buffett", "technical_analyst"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI",
    "initial_cash": 50000,
    "start_date": start_date.strftime("%Y-%m-%d"),
    "end_date": end_date.strftime("%Y-%m-%d")
}

# Stream the response
with requests.post(url, json=payload, headers=headers, stream=True) as response:
    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("data:"):
            data = json.loads(line.split(":", 1)[1].strip())
            print(f"Event: {data}")
```

**Enhanced Streaming Output:**
```
Event 1: start
✅ Analysis started

Event 3: progress
📊 warren_buffett_agent analyzing AAPL: Fetching financial metrics

Event 5: progress
📊 technical_analyst_agent analyzing AAPL: Analyzing price data

Event 7: progress
📊 warren_buffett_agent analyzing AAPL: Gathering financial line items

Event 25: progress
📊 warren_buffett_agent analyzing AAPL: Getting market cap

Event 27: progress
📊 warren_buffett_agent analyzing AAPL: Analyzing fundamentals

Event 29: progress
📊 warren_buffett_agent analyzing AAPL: Analyzing consistency

Event 31: progress
📊 warren_buffett_agent analyzing AAPL: Analyzing moat

Event 33: progress
📊 warren_buffett_agent analyzing AAPL: Analyzing management quality

Event 35: progress
📊 warren_buffett_agent analyzing AAPL: Calculating intrinsic value

Event 37: progress
📊 warren_buffett_agent analyzing AAPL: Generating Warren Buffett analysis

Event 59: complete
🎯 Analysis complete!
📈 AAPL: SHORT 49 shares (85.0% confidence)
💭 Reasoning: Both the technical analyst agent and Warren Buffett agent have a bearish outlook on AAPL, with Warren Buffett finding it overvalued...
```

---

## 📋 Request Parameters Reference

### HedgeFundRequest Schema

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `tickers` | array[string] | Yes | - | Stock symbols (e.g., ["AAPL", "MSFT"]) |
| `selected_agents` | array[string] | Yes | - | Agent IDs from `/agents` endpoint |
| `model_name` | string | No | "gpt-4o" | LLM model name |
| `model_provider` | string | No | "OpenAI" | Model provider (OpenAI, Anthropic, etc.) |
| `initial_cash` | float | No | 100000.0 | Starting cash amount |
| `margin_requirement` | float | No | 0.0 | Margin requirement |
| `start_date` | string | No | 3 months ago | Analysis start date (YYYY-MM-DD) |
| `end_date` | string | No | Today | Analysis end date (YYYY-MM-DD) |
| `show_reasoning` | boolean | No | false | Show detailed AI reasoning (like CLI --show-reasoning) |

### Model Provider Values

Use exact case-sensitive values:
- `"OpenAI"` ✅ (not "OPENAI" ❌)
- `"Anthropic"`
- `"DeepSeek"`
- `"Gemini"`
- `"Groq"`

---

## 🎯 Analysis Decision Types

### Action Types
- **`"buy"`** - Purchase shares (bullish)
- **`"sell"`** - Sell existing shares
- **`"short"`** - Short sell shares (bearish)
- **`"hold"`** - No position change (neutral)

### Confidence Levels
- **0-30%** - Low confidence
- **30-70%** - Medium confidence  
- **70-100%** - High confidence

---

## 🐛 Troubleshooting

### Common Issues

1. **404 on `/health`**
   - Check if API server is running
   - Verify URL: `http://localhost:8000/health`

2. **"Response ended prematurely"**
   - Normal for quick analyses
   - Try multiple agents for longer streams
   - Check API keys in `.env` file

3. **Enum validation error**
   - Use correct case: `"OpenAI"` not `"OPENAI"`
   - Check `/models` endpoint for valid providers

4. **Timeout errors**
   - Increase timeout for complex analyses
   - Use fewer tickers/agents for testing

### Debug Commands

```bash
# Check server status
curl http://localhost:8000/

# Test simple endpoint
curl http://localhost:8000/health

# Validate JSON
echo '{"test": "json"}' | python -m json.tool

# Check API server logs
poetry run python app/backend/run_api.py
```

---

## 📚 Postman Collection

Import the pre-configured collection:
```bash
# Location: app/backend/postman_collection.json
```

**Collection includes:**
- Health check requests
- Agent/model discovery
- Synchronous analysis examples
- Streaming endpoint tests

---

## 🚀 Advanced Usage

### Multiple Tickers + Multiple Agents

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
  "selected_agents": [
    "warren_buffett",
    "peter_lynch", 
    "technical_analyst",
    "michael_burry"
  ],
  "model_name": "gpt-4o",
  "model_provider": "OpenAI",
  "initial_cash": 200000,
  "margin_requirement": 10000
}
```

### Historical Analysis

```json
{
  "tickers": ["SPY", "QQQ"],
  "selected_agents": ["warren_buffett", "technical_analyst"],
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "model_name": "claude-3-5-haiku-latest",
  "model_provider": "Anthropic"
}
```

---

## 📈 Performance Tips

### For Faster Responses:
- Use 1-2 tickers max
- Select 1-2 agents
- Use `gpt-4o-mini` or `claude-3-5-haiku-latest`
- Shorter date ranges (7-30 days)

### For Comprehensive Analysis:
- Use 3-5 tickers
- Mix agent types (value + growth + technical)
- Use `gpt-4o` or `claude-sonnet-4`
- Longer historical periods (3-12 months)

---

## 🎯 Real-World Examples

### Value Investing Focus
```json
{
  "selected_agents": ["warren_buffett", "ben_graham", "charlie_munger"],
  "tickers": ["BRK-B", "KO", "JNJ"]
}
```

### Growth Investing Focus  
```json
{
  "selected_agents": ["cathie_wood", "peter_lynch", "phil_fisher"],
  "tickers": ["TSLA", "NVDA", "AMZN"]
}
```

### Technical Analysis Focus
```json
{
  "selected_agents": ["technical_analyst", "stanley_druckenmiller"],
  "tickers": ["SPY", "QQQ", "IWM"]
}
```

---

## 📞 API Summary

The AI Hedge Fund API successfully transforms a CLI-based system into a modern web API with:

- ✅ **RESTful endpoints** for all functionality
- ✅ **Real-time streaming** with Server-Sent Events  
- ✅ **Multiple AI agents** with unique investment philosophies
- ✅ **Comprehensive analysis** including technical and fundamental factors
- ✅ **Production-ready** with proper error handling and documentation

**Total transformation:** From command-line prompts to HTTP API calls! 🚀 