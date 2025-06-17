# AI Hedge Fund API Documentation

## Overview

The AI Hedge Fund API provides a RESTful interface to interact with the AI-powered hedge fund trading system. Instead of using command-line arguments, you can now make HTTP requests to analyze stocks and get trading recommendations.

## Getting Started

### 1. Start the API Server

```bash
# From the project root directory
python app/backend/run_api.py

# Or using uvicorn directly
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 2. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### 1. Health Check

Check if the API is running.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-03-20T10:30:00Z"
}
```

### 2. Get Available Agents

List all available AI analyst agents.

```http
GET /hedge-fund/agents
```

**Response:**
```json
{
  "agents": [
    {"id": "technical_analyst", "name": "Technical Analyst"},
    {"id": "fundamental_analyst", "name": "Fundamental Analyst"},
    {"id": "sentiment_analyst", "name": "Sentiment Analyst"},
    {"id": "risk_analyst", "name": "Risk Analyst"},
    {"id": "portfolio_analyst", "name": "Portfolio Analyst"},
    {"id": "market_regime_analyst", "name": "Market Regime Analyst"},
    {"id": "news_analyst", "name": "News Analyst"},
    {"id": "sector_analyst", "name": "Sector Analyst"}
  ]
}
```

### 3. Get Available Models

List all available LLM models.

```http
GET /hedge-fund/models
```

**Response:**
```json
{
  "models": [
    {
      "display_name": "OpenAI GPT-4o",
      "model_name": "gpt-4o",
      "provider": "OPENAI"
    },
    {
      "display_name": "Anthropic Claude 3.5 Sonnet",
      "model_name": "gpt-4o",
      "provider": "ANTHROPIC"
    }
    // ... more models
  ]
}
```

### 4. Run Hedge Fund Analysis (Synchronous)

Run the hedge fund analysis and get results in a single response. Best for testing with Postman.

```http
POST /hedge-fund/run-sync
Content-Type: application/json

{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "selected_agents": ["technical_analyst", "fundamental_analyst", "sentiment_analyst"],
  "model_name": "gpt-4o",
  "model_provider": "OPENAI",
  "initial_cash": 100000,
  "margin_requirement": 0,
  "start_date": "2024-01-01",  // Optional, defaults to 3 months ago
  "end_date": "2024-03-31"     // Optional, defaults to today
}
```

**Response:**
```json
{
  "decisions": {
    "AAPL": {
      "action": "buy",
      "quantity": 150,
      "confidence": 0.85,
      "reasoning": "Strong technical indicators and positive sentiment"
    },
    "MSFT": {
      "action": "hold",
      "quantity": 0,
      "confidence": 0.7,
      "reasoning": "Neutral outlook, waiting for better entry point"
    },
    "GOOGL": {
      "action": "sell",
      "quantity": 50,
      "confidence": 0.75,
      "reasoning": "Overvalued based on fundamental analysis"
    }
  },
  "analyst_signals": {
    "technical_analyst": { /* technical analysis results */ },
    "fundamental_analyst": { /* fundamental analysis results */ },
    "sentiment_analyst": { /* sentiment analysis results */ }
  },
  "metadata": {
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "model": "OPENAI:gpt-4o",
    "selected_agents": ["technical_analyst", "fundamental_analyst", "sentiment_analyst"]
  }
}
```

### 5. Run Hedge Fund Analysis (Streaming)

Run the hedge fund analysis with real-time progress updates via Server-Sent Events.

```http
POST /hedge-fund/run
Content-Type: application/json

{
  "tickers": ["AAPL", "MSFT"],
  "selected_agents": ["technical_analyst", "risk_analyst"],
  "model_name": "gpt-4o",
  "model_provider": "OPENAI",
  "initial_cash": 50000,
  "margin_requirement": 0
}
```

**Response:** Server-Sent Events stream
```
event: start
data: {"message": "Starting hedge fund analysis"}

event: progress
data: {"agent": "technical_analyst", "ticker": "AAPL", "status": "analyzing", "timestamp": "2024-03-20T10:30:00Z"}

event: progress
data: {"agent": "technical_analyst", "ticker": "MSFT", "status": "analyzing", "timestamp": "2024-03-20T10:30:05Z"}

event: complete
data: {"decisions": {...}, "analyst_signals": {...}}
```

## Using with Postman

### Import the Collection

1. Open Postman
2. Click "Import" → "File"
3. Select `app/backend/postman_collection.json`
4. The collection includes pre-configured requests for all endpoints

### Environment Variables

Set these in your Postman environment:
- `base_url`: `http://localhost:8000`

### Testing Workflow

1. **Check API Health**: Run the "Health Check" request
2. **Get Available Options**: Run "Get Available Agents" and "Get Available Models"
3. **Run Analysis**: Use the agent IDs and model names in the "Run Hedge Fund Analysis" request

## Request Parameters

### HedgeFundRequest Schema

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `tickers` | array[string] | Yes | - | Stock symbols to analyze (e.g., ["AAPL", "MSFT"]) |
| `selected_agents` | array[string] | Yes | - | Agent IDs to use for analysis |
| `model_name` | string | No | "gpt-4o" | LLM model name |
| `model_provider` | string | No | "OPENAI" | Model provider (OPENAI, ANTHROPIC, etc.) |
| `initial_cash` | float | No | 100000.0 | Starting cash amount |
| `margin_requirement` | float | No | 0.0 | Margin requirement for trading |
| `start_date` | string | No | 3 months ago | Analysis start date (YYYY-MM-DD) |
| `end_date` | string | No | Today | Analysis end date (YYYY-MM-DD) |

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Successful request
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Authentication

Currently, the API does not require authentication. In production, you should implement:
- API key authentication
- JWT tokens
- Rate limiting

## CORS Configuration

By default, CORS is configured to allow all origins (`*`) for development. Update this in production to restrict to your frontend domains.

## Environment Variables

Create a `.env` file in the project root:

```env
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key

# Financial Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINANCIAL_MODELING_PREP_API_KEY=your_fmp_key

# Server Configuration
PORT=8000
HOST=0.0.0.0
```

## Example: Complete Workflow in Python

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# 1. Check health
health = requests.get(f"{BASE_URL}/health").json()
print(f"API Status: {health['status']}")

# 2. Get available agents
agents = requests.get(f"{BASE_URL}/hedge-fund/agents").json()
agent_ids = [agent['id'] for agent in agents['agents'][:3]]  # Select first 3

# 3. Get available models
models = requests.get(f"{BASE_URL}/hedge-fund/models").json()

# 4. Run analysis
payload = {
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "selected_agents": agent_ids,
    "model_name": "gpt-4o",
    "model_provider": "OPENAI",
    "initial_cash": 100000
}

response = requests.post(
    f"{BASE_URL}/hedge-fund/run-sync",
    json=payload
)

result = response.json()
print(json.dumps(result, indent=2))
```

## Next Steps

1. **Deploy to Production**: Use the existing Docker setup or deploy to cloud platforms
2. **Add Authentication**: Implement API key or JWT authentication
3. **Add Rate Limiting**: Prevent API abuse
4. **Implement Caching**: Cache analysis results for frequently requested tickers
5. **Add WebSocket Support**: For real-time portfolio updates
6. **Create Frontend**: Build a web interface to interact with the API 