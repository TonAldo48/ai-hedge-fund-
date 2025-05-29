# AI Hedge Fund API - Quick Reference

## 🚀 Start Server
```bash
poetry run python app/backend/run_api.py
```
**API URL:** http://localhost:8000  
**Docs:** http://localhost:8000/docs

---

## 🔍 Discovery Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Available Agents
```bash
curl http://localhost:8000/hedge-fund/agents
```
**Popular agents:** `warren_buffett`, `peter_lynch`, `technical_analyst`, `michael_burry`

### Available Models
```bash
curl http://localhost:8000/hedge-fund/models
```
**Popular models:** `gpt-4o`, `gpt-4o-mini`, `claude-3-5-haiku-latest`

---

## 📊 Quick Analysis (Synchronous)

### Single Stock + Single Agent
```bash
curl -X POST "http://localhost:8000/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["warren_buffett"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI"
  }'
```

### Multi-Stock Portfolio
```bash
curl -X POST "http://localhost:8000/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "selected_agents": ["warren_buffett", "technical_analyst"],
    "model_name": "gpt-4o",
    "model_provider": "OpenAI",
    "initial_cash": 100000
  }'
```

---

## 🌊 Real-Time Analysis (Streaming)

### Basic Streaming
```bash
curl -X POST "http://localhost:8000/hedge-fund/run" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["technical_analyst"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI"
  }' \
  --no-buffer
```

### Enhanced Streaming (Multiple Agents)
```bash
curl -X POST "http://localhost:8000/hedge-fund/run" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "tickers": ["AAPL", "MSFT", "NVDA"],
    "selected_agents": ["warren_buffett", "technical_analyst"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI",
    "initial_cash": 50000,
    "start_date": "2025-05-18",
    "end_date": "2025-05-28"
  }' \
  --no-buffer
```

---

## 📋 Essential Parameters

| Parameter | Example | Notes |
|-----------|---------|-------|
| `tickers` | `["AAPL", "MSFT"]` | Stock symbols |
| `selected_agents` | `["warren_buffett", "technical_analyst"]` | Agent IDs |
| `model_provider` | `"OpenAI"` | Case-sensitive! |
| `model_name` | `"gpt-4o-mini"` | Check `/models` endpoint |
| `initial_cash` | `50000` | Portfolio starting cash |
| `show_reasoning` | `true` | **NEW!** Detailed AI reasoning (like CLI `--show-reasoning`) |

---

## 🎯 Response Format

### Sync Response
```json
{
  "decisions": {
    "AAPL": {
      "action": "buy",        // buy/sell/short/hold
      "quantity": 125,        // Number of shares
      "confidence": 85.0,     // 0-100% confidence
      "reasoning": "..."      // AI explanation
    }
  }
}
```

### Streaming Events
```
event: progress
data: {"type":"progress","agent":"warren_buffett_agent","ticker":"AAPL","status":"Analyzing fundamentals"}

event: complete  
data: {"type":"complete","data":{"decisions":{...}}}
```

---

## ⚡ Agent Combinations

### Value Investing
```json
{"selected_agents": ["warren_buffett", "ben_graham", "charlie_munger"]}
```

### Growth Investing
```json
{"selected_agents": ["cathie_wood", "peter_lynch", "phil_fisher"]}
```

### Technical Analysis
```json
{"selected_agents": ["technical_analyst", "stanley_druckenmiller"]}
```

### Comprehensive Analysis
```json
{"selected_agents": ["warren_buffett", "technical_analyst", "peter_lynch"]}
```

---

## 🐛 Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| 404 on `/health` | Check server running: `poetry run python app/backend/run_api.py` |
| "Response ended prematurely" | Use multiple agents or longer date range |
| Enum validation error | Use exact case: `"OpenAI"` not `"OPENAI"` |
| Timeout | Use fewer tickers/agents or lighter models |

---

## 📁 Files Created

- `API_INTERACTION_GUIDE.md` - Full documentation with examples
- `postman_collection.json` - Ready-to-import Postman collection  
- `test_streaming.py` - Python streaming test script
- `API_DOCUMENTATION.md` - Technical API reference

**Ready to analyze! 🚀** 

## 🧠 Detailed Reasoning (NEW!)

### With Reasoning Flag
```bash
curl -X POST "http://localhost:8000/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["warren_buffett"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI",
    "show_reasoning": true
  }'
```

**Enhanced Response:** More detailed `reasoning` fields in `analyst_signals` section. 