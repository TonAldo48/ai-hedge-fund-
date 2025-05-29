# AI Hedge Fund API Backend

This is the FastAPI backend that exposes the AI Hedge Fund functionality as a REST API.

## Quick Start

### 1. Install Dependencies

Make sure you have installed all dependencies:
```bash
# Using poetry (recommended)
poetry install

# Or using pip
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root with your API keys:
```env
# Required API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Financial Data APIs
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINANCIAL_MODELING_PREP_API_KEY=your_fmp_key

# Optional
GROQ_API_KEY=your_groq_key
DEEPSEEK_API_KEY=your_deepseek_key
```

### 3. Run the API Server

```bash
# From project root
python app/backend/run_api.py

# Or using uvicorn directly
uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 5. Test with Postman

1. Import the Postman collection: `app/backend/postman_collection.json`
2. Test the endpoints:
   - `GET /health` - Check API status
   - `GET /hedge-fund/agents` - List available AI agents
   - `GET /hedge-fund/models` - List available LLM models
   - `POST /hedge-fund/run-sync` - Run analysis (synchronous)
   - `POST /hedge-fund/run` - Run analysis (streaming)

### Example Request

```bash
curl -X POST "http://localhost:8000/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT"],
    "selected_agents": ["technical_analyst", "fundamental_analyst"],
    "model_name": "gpt-4o",
    "model_provider": "OPENAI",
    "initial_cash": 100000
  }'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message |
| `/health` | GET | Health check |
| `/hedge-fund/agents` | GET | List available AI agents |
| `/hedge-fund/models` | GET | List available LLM models |
| `/hedge-fund/run-sync` | POST | Run analysis (synchronous) |
| `/hedge-fund/run` | POST | Run analysis (streaming) |

## Development

### Running with Docker

```bash
# Build the image
docker build -t ai-hedge-fund-api .

# Run the container
docker run -p 8000:8000 --env-file .env ai-hedge-fund-api
```

### Testing

```bash
# Run tests
pytest app/backend/tests/

# Run with coverage
pytest --cov=app.backend app/backend/tests/
```

## Deployment

The API is ready for deployment to:
- **Railway**: Connect GitHub repo, auto-deploys
- **Render**: Free tier available
- **Google Cloud Run**: Serverless, scales to zero
- **AWS App Runner**: Fully managed
- **Heroku**: Easy deployment

See `API_DOCUMENTATION.md` for detailed deployment instructions.

## Architecture

```
app/backend/
├── main.py           # FastAPI app initialization
├── run_api.py        # Standalone server script
├── models/           # Pydantic models
│   ├── schemas.py    # Request/response schemas
│   └── events.py     # SSE event models
├── routes/           # API endpoints
│   ├── health.py     # Health check
│   └── hedge_fund.py # Main hedge fund endpoints
└── services/         # Business logic
    ├── graph.py      # LangGraph integration
    └── portfolio.py  # Portfolio management
```

## Troubleshooting

### Common Issues

1. **API Keys Missing**: Ensure all required API keys are in `.env`
2. **Port Already in Use**: Change port with `PORT=8001 python app/backend/run_api.py`
3. **Import Errors**: Run from project root, not from `app/backend/`
4. **CORS Issues**: Update allowed origins in `main.py` for production

### Debug Mode

Enable debug logging:
```bash
LOG_LEVEL=DEBUG python app/backend/run_api.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

See LICENSE file in the project root.