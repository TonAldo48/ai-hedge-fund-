# 🚀 AI Hedge Fund Backend API

A FastAPI-based backend for AI-powered hedge fund analysis and backtesting with real-time streaming capabilities.

## 🌟 Features

- **🤖 AI-Powered Analysis**: Multiple AI analyst agents (Warren Buffett, Michael Burry, etc.)
- **📊 Real-time Backtesting**: Stream live backtest updates via Server-Sent Events
- **🔐 Production Authentication**: API key-based security
- **⚡ High Performance**: Async/await with FastAPI
- **📱 CORS Support**: Ready for frontend integration
- **🔄 Multiple LLM Support**: OpenAI, Anthropic, DeepSeek integration

## 📡 API Endpoints

### Core Hedge Fund Analysis
- `POST /hedge-fund/run-sync` - Synchronous analysis
- `POST /hedge-fund/run` - Streaming analysis
- `GET /hedge-fund/agents` - Available AI agents
- `GET /hedge-fund/models` - Supported LLM models

### **NEW: Backtesting API** 🎯
- `POST /backtest/start` - Start streaming backtest
- `GET /backtest/stream/{id}` - Real-time backtest updates
- `GET /backtest/status/{id}` - Check backtest status
- `POST /backtest/run-sync` - Synchronous backtest
- `DELETE /backtest/{id}` - Cancel running backtest

### Utility
- `GET /` - API information
- `GET /health` - Health check

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**:
```bash
pip install fastapi uvicorn python-dotenv
```

2. **Set Environment Variables**:
```bash
export OPENAI_API_KEY="your-openai-key"
export API_KEY="your-api-key"  # Optional for auth
```

3. **Run the Server**:
```bash
cd app
python -m backend.run_api
```

4. **Access the API**:
- API: http://localhost:8000
- Docs: https://aeeroooo-production.up.railway.app/docs
- Health: https://aeeroooo-production.up.railway.app/health

### Railway Deployment

1. **Environment Variables**:
```bash
OPENAI_API_KEY=your-openai-key
API_KEY=your-hedge-fund-api-key
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000
```

2. **Start Command**:
```bash
cd app && python -m backend.run_api
```

## 📚 Documentation

- **[Backtesting API Guide](./BACKTESTING_API_GUIDE.md)** - Complete guide for backtesting features
- **[API Documentation](./API_DOCUMENTATION.md)** - General API reference
- **[Quick Reference](./API_QUICK_REFERENCE.md)** - Quick command examples

## 🧪 Testing

Run the comprehensive test suite:

```bash
cd app/backend

# Test streaming backtest
python tests/test_backtest_api.py

# Test synchronous backtest  
python tests/test_backtest_api.py sync

# Test general API
python tests/test_api.py
```

## 🔐 Authentication

The API supports two authentication methods:

1. **Header Method**:
```bash
curl -H "X-API-Key: your-api-key" ...
```

2. **Bearer Token**:
```bash
curl -H "Authorization: Bearer your-api-key" ...
```

**Development Mode**: If no `API_KEY` environment variable is set, authentication is disabled.

## 🤖 AI Agents

| Agent | Strategy | Use Case |
|-------|----------|----------|
| `warren_buffett` | Value investing | Long-term quality stocks |
| `peter_lynch` | Growth analysis | High-growth companies |
| `ray_dalio` | Macro-economic | Economic trends |
| `michael_burry` | Contrarian/Short | Market inefficiencies |
| `cathie_wood` | Innovation focus | Disruptive technology |
| `technical_analyst` | Technical indicators | Chart patterns |

## 📊 Supported Models

- **OpenAI**: gpt-4o-mini, gpt-4o-mini-mini, gpt-4o-mini-mini
- **Anthropic**: claude-3-5-sonnet, claude-3-haiku
- **DeepSeek**: deepseek-chat, deepseek-reasoner

## 🌐 Frontend Integration

### JavaScript Example
```javascript
// Start backtest
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
    initial_capital: 100000
  })
});

const { backtest_id } = await response.json();

// Stream updates
const eventSource = new EventSource(`/backtest/stream/${backtest_id}`);
eventSource.addEventListener('backtest_progress', (event) => {
  const data = JSON.parse(event.data);
  console.log(`Progress: ${data.progress * 100}%`);
});
```

## 📁 Project Structure

```
app/backend/
├── main.py                 # FastAPI app
├── run_api.py             # Server startup script
├── routes/                # API endpoints
│   ├── hedge_fund.py      # Core analysis routes
│   ├── backtester.py      # Backtesting routes
│   └── health.py          # Utility routes
├── services/              # Business logic
│   ├── backtester.py      # Streaming backtester
│   ├── graph.py           # Agent workflow
│   └── portfolio.py       # Portfolio management
├── models/                # Data models
│   ├── schemas.py         # Request/response models
│   └── events.py          # SSE event models
├── middleware/            # API middleware
│   └── auth.py           # Authentication
└── tests/                # Test suite
    ├── test_backtest_api.py
    └── test_api.py
```

## ⚡ Performance

- **Async/Await**: Non-blocking request handling
- **Thread Pool**: CPU-intensive tasks run in background
- **SSE Streaming**: Real-time updates without polling
- **Event Queue**: Efficient event distribution

## 🔧 Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `API_KEY` | Hedge fund API key | None (disables auth) |
| `ENVIRONMENT` | Environment mode | development |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the `app/` directory
2. **Authentication Failures**: Check `API_KEY` environment variable
3. **SSE Connection Issues**: Verify CORS settings for your frontend domain
4. **Model Errors**: Confirm `OPENAI_API_KEY` is valid

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=debug
python -m backend.run_api
```

## 📈 Roadmap

- [ ] WebSocket support for bidirectional communication
- [ ] Multi-timeframe backtesting
- [ ] Portfolio optimization algorithms
- [ ] Risk management constraints
- [ ] Custom strategy scripting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add comprehensive tests
4. Update documentation
5. Submit a pull request

## 📞 Support

- **API Docs**: Visit `/docs` for interactive documentation
- **Health Check**: Use `/health` to verify server status
- **Issues**: Report bugs in the GitHub repository