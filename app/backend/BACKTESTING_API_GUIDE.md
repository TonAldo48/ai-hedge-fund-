# 🚀 AI Hedge Fund Backtesting API Guide

## Overview

The Backtesting API allows you to run AI-powered trading simulations with real-time streaming updates. The API supports multiple AI analyst agents, various time periods, and provides comprehensive performance metrics.

## 🔐 Authentication

All backtesting endpoints require authentication via API key:

```bash
# Header method
curl -H "X-API-Key: your-api-key" ...

# Bearer token method  
curl -H "Authorization: Bearer your-api-key" ...
```

## 📡 API Endpoints

### 1. Start Backtest (Streaming)

**POST** `/backtest/start`

Start a new backtest session that can be streamed in real-time.

#### Request Body:
```json
{
  "tickers": ["AAPL", "MSFT"],
  "selected_agents": ["michael_burry", "cathie_wood"],
  "start_date": "2025-05-15",
  "end_date": "2025-05-29", 
  "model_name": "gpt-4o-mini",
  "model_provider": "OpenAI",
  "initial_capital": 100000,
  "margin_requirement": 0.0,
  "show_reasoning": true
}
```

#### Response:
```json
{
  "backtest_id": "870eac14-8958-452b-9ff3-cb7477ccb685",
  "status": "started",
  "message": "Backtest started successfully",
  "stream_url": "/backtest/stream/870eac14-8958-452b-9ff3-cb7477ccb685",
  "status_url": "/backtest/status/870eac14-8958-452b-9ff3-cb7477ccb685"
}
```

### 2. Stream Backtest Updates

**GET** `/backtest/stream/{backtest_id}`

Stream real-time updates using Server-Sent Events (SSE).

#### Event Types:

##### `backtest_start`
```json
{
  "type": "backtest_start",
  "backtest_id": "...",
  "total_days": 11,
  "tickers": ["AAPL", "MSFT"],
  "timestamp": "2025-05-29T08:49:15.123Z"
}
```

##### `backtest_progress`
```json
{
  "type": "backtest_progress", 
  "backtest_id": "...",
  "current_date": "2025-05-15",
  "progress": 0.091,
  "completed_days": 1,
  "total_days": 11,
  "message": "Processing 2025-05-15",
  "timestamp": "2025-05-29T08:49:16.456Z"
}
```

##### `trading`
```json
{
  "type": "trading",
  "backtest_id": "...",
  "date": "2025-05-16", 
  "ticker": "AAPL",
  "action": "short",
  "quantity": 94,
  "price": 211.45,
  "portfolio_value": 100000.0,
  "timestamp": "2025-05-29T08:49:18.789Z"
}
```

##### `portfolio_update`
```json
{
  "type": "portfolio_update",
  "backtest_id": "...",
  "date": "2025-05-16",
  "cash": 100000.0,
  "total_value": 100000.0,
  "daily_return": 0.0,
  "positions": {
    "AAPL": {"long": 0, "short": 94},
    "MSFT": {"long": 0, "short": 44}
  },
  "timestamp": "2025-05-29T08:49:19.012Z"
}
```

##### `performance_update`
```json
{
  "type": "performance_update",
  "backtest_id": "...",
  "sharpe_ratio": -9.83,
  "sortino_ratio": 4.86,
  "max_drawdown": -0.14,
  "total_return": -0.11,
  "timestamp": "2025-05-29T08:49:20.345Z"
}
```

##### `backtest_complete`
```json
{
  "type": "backtest_complete",
  "backtest_id": "...",
  "final_performance": {
    "total_return": -0.11,
    "final_value": 99891.68,
    "initial_capital": 100000.0,
    "sharpe_ratio": -9.83,
    "max_drawdown": -0.14
  },
  "timestamp": "2025-05-29T08:49:45.345Z"
}
```

### 3. Get Backtest Status

**GET** `/backtest/status/{backtest_id}`

Get current status of a running or completed backtest.

#### Response:
```json
{
  "backtest_id": "...",
  "status": "running",
  "progress": 0.45,
  "current_date": "2025-05-20", 
  "start_time": "2025-05-29T08:49:15.123Z",
  "is_running": true,
  "error_message": null,
  "request_summary": {
    "tickers": ["AAPL", "MSFT"],
    "agents": ["michael_burry", "cathie_wood"],
    "start_date": "2025-05-15",
    "end_date": "2025-05-29",
    "initial_capital": 100000
  }
}
```

### 4. Run Synchronous Backtest

**POST** `/backtest/run-sync`

⚠️ **Warning**: Blocking endpoint - use streaming version for better UX.

#### Request Body:
Same as `/backtest/start`

#### Response:
```json
{
  "status": "completed",
  "performance_metrics": {
    "total_return": -0.11,
    "final_value": 99891.68,
    "initial_capital": 100000.0,
    "sharpe_ratio": -9.83,
    "sortino_ratio": 4.86,
    "max_drawdown": -0.14
  },
  "portfolio_history": [
    {"date": "2025-05-15", "value": 100000.0},
    {"date": "2025-05-16", "value": 99998.42}
  ],
  "final_portfolio": {
    "cash": 99891.68,
    "positions": {...},
    "realized_gains": {...}
  }
}
```

### 5. Cancel Backtest

**DELETE** `/backtest/{backtest_id}`

Cancel a running backtest.

#### Response:
```json
{
  "backtest_id": "...",
  "status": "cancelled", 
  "message": "Backtest cancelled successfully"
}
```

## 🤖 Available Agents

- `warren_buffett` - Value investing approach
- `peter_lynch` - Growth stock analysis  
- `ray_dalio` - Macro-economic analysis
- `michael_burry` - Contrarian/short analysis
- `cathie_wood` - Innovation/tech focus
- `technical_analyst` - Technical indicators

## 📊 Supported Models

- **OpenAI**: `gpt-4o`, `gpt-4o-mini`
- **Anthropic**: `gpt-4o`, `claude-3-haiku-20240307`
- **DeepSeek**: `deepseek-chat`, `deepseek-reasoner`

## 🌐 Frontend Integration

### JavaScript EventSource Example

```javascript
const streamBacktest = async (backtestId) => {
  // Start the backtest
  const response = await fetch('/backtest/start', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': 'your-api-key'
    },
    body: JSON.stringify({
      tickers: ['AAPL', 'MSFT'],
      selected_agents: ['michael_burry', 'cathie_wood'],
      start_date: '2025-05-15',
      end_date: '2025-05-29',
      model_name: 'gpt-4o-mini',
      model_provider: 'OpenAI',
      initial_capital: 100000
    })
  });
  
  const { backtest_id } = await response.json();
  
  // Connect to stream
  const eventSource = new EventSource(
    `/backtest/stream/${backtest_id}`,
    {
      headers: {
        'X-API-Key': 'your-api-key'
      }
    }
  );
  
  // Handle events
  eventSource.addEventListener('backtest_progress', (event) => {
    const data = JSON.parse(event.data);
    updateProgressBar(data.progress);
  });
  
  eventSource.addEventListener('trading', (event) => {
    const data = JSON.parse(event.data);
    addTradeToFeed(data);
  });
  
  eventSource.addEventListener('backtest_complete', (event) => {
    const data = JSON.parse(event.data);
    showResults(data.final_performance);
    eventSource.close();
  });
};
```

### React Hook Example

```jsx
import { useState, useEffect } from 'react';

const useBacktestStream = (backtestId, apiKey) => {
  const [progress, setProgress] = useState(0);
  const [trades, setTrades] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!backtestId) return;

    const eventSource = new EventSource(
      `/backtest/stream/${backtestId}`,
      { headers: { 'X-API-Key': apiKey } }
    );

    eventSource.addEventListener('backtest_progress', (event) => {
      const data = JSON.parse(event.data);
      setProgress(data.progress);
    });

    eventSource.addEventListener('trading', (event) => {
      const data = JSON.parse(event.data);
      setTrades(prev => [...prev, data]);
    });

    eventSource.addEventListener('portfolio_update', (event) => {
      const data = JSON.parse(event.data);
      setPortfolio(data);
    });

    eventSource.addEventListener('backtest_complete', (event) => {
      setIsComplete(true);
      eventSource.close();
    });

    return () => eventSource.close();
  }, [backtestId, apiKey]);

  return { progress, trades, portfolio, isComplete };
};
```

## 📈 UI Components You Can Build

1. **Real-time Progress Bar**: `progress` field (0.0 to 1.0)
2. **Live Trading Feed**: Stream of `trading` events
3. **Portfolio Value Chart**: Time series from `portfolio_update.total_value`
4. **Performance Dashboard**: Metrics from `performance_update`
5. **Position Tracker**: Current holdings from `portfolio.positions`
6. **Daily Returns**: `daily_return` from portfolio updates

## ⚡ Best Practices

1. **Use Streaming**: Prefer `/backtest/start` + `/backtest/stream/{id}` over `/backtest/run-sync`
2. **Handle Reconnection**: Implement reconnection logic for SSE failures
3. **Graceful Degradation**: Fall back to polling `/backtest/status/{id}` if SSE fails
4. **Cancel Running Jobs**: Use `DELETE /backtest/{id}` to clean up resources
5. **Error Handling**: Listen for `error` events in SSE stream

## 🚀 Production Deployment

When deploying to Railway:

1. Set environment variables:
   ```bash
   OPENAI_API_KEY=your-openai-key
   API_KEY=your-hedge-fund-api-key
   ENVIRONMENT=production
   ```

2. The API will be available at:
   ```
   https://your-app.railway.app/backtest/*
   ```

3. Update CORS settings for your frontend domain in `main.py`

## 🔍 Testing

Use the included test script:
```bash
cd app/backend
python test_backtest_api.py        # Test streaming
python test_backtest_api.py sync   # Test synchronous
```

## 📞 Support

For issues or questions about the Backtesting API, check:
- API docs: `/docs` endpoint
- Health check: `/health` endpoint
- Available agents: `/hedge-fund/agents`
- Available models: `/hedge-fund/models` 