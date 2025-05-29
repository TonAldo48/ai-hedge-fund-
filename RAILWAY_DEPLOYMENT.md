# Railway Deployment Guide

## 🚀 Deploy AI Hedge Fund API to Railway

This guide will help you deploy your AI hedge fund API to Railway for production use with proper authentication and security.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **API Keys**: Have your API keys ready for environment variables
4. **Authentication Key**: Generate a secure API key for client authentication

## 🛠️ Deployment Steps

### 1. Generate API Authentication Key

First, generate a secure API key for client authentication:

```bash
# Generate a secure API key
python generate_api_key.py

# Example output:
# Generated API Key: K7x9mN2pQ8vR3uT6yE4wA1sD5fG8hJ0kL2nM9pQ7rT4vY6zB3cF1gH8jK5nM2pQ9
```

**Important**: Save this key securely - you'll need it for Railway environment variables and client requests.

### 2. Connect to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your AI hedge fund repository

### 3. Configure Build Settings

Railway will automatically detect the `railway.toml` configuration:
- **Dockerfile**: `Dockerfile.api`
- **Port**: 8000
- **Health Check**: `/health` endpoint

### 4. Set Environment Variables

In your Railway project dashboard, go to **Variables** and add:

#### Required API Keys:
```bash
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
```

#### **🔐 Authentication (CRITICAL):**
```bash
API_KEY=your-generated-api-key-from-step-1
```

#### Optional Settings:
```bash
PORT=8000
HOST=0.0.0.0
PYTHONUNBUFFERED=1
ENVIRONMENT=production
```

### 5. Deploy

1. Click **"Deploy"** in Railway
2. Wait for the build to complete (2-5 minutes)
3. Your API will be available at: `https://your-app-name.railway.app`

## 🔍 Testing Your Deployed API

### Public Endpoints (No Authentication Required)

```bash
# Health Check
curl https://your-app-name.railway.app/health

# List Agents
curl https://your-app-name.railway.app/hedge-fund/agents

# List Models
curl https://your-app-name.railway.app/hedge-fund/models
```

### Protected Endpoints (Authentication Required)

#### Method 1: X-API-Key Header
```bash
curl -X POST "https://your-app-name.railway.app/hedge-fund/run-sync" \
  -H "X-API-Key: your-generated-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["warren_buffett"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI",
    "show_reasoning": true
  }'
```

#### Method 2: Bearer Token
```bash
curl -X POST "https://your-app-name.railway.app/hedge-fund/run-sync" \
  -H "Authorization: Bearer your-generated-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["warren_buffett"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI",
    "show_reasoning": true
  }'
```

### Test Streaming with Authentication
```bash
curl -X POST "https://your-app-name.railway.app/hedge-fund/run" \
  -H "X-API-Key: your-generated-api-key" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "tickers": ["AAPL", "MSFT"],
    "selected_agents": ["warren_buffett", "technical_analyst"],
    "model_name": "gpt-4o",
    "model_provider": "OpenAI"
  }' \
  --no-buffer
```

## 📊 API Endpoints

| Endpoint | Method | Authentication | Description |
|----------|--------|----------------|-------------|
| `/` | GET | None | API information |
| `/health` | GET | None | Health check |
| `/docs` | GET | None | Interactive API documentation |
| `/hedge-fund/agents` | GET | Optional | List available agents |
| `/hedge-fund/models` | GET | Optional | List available models |
| `/hedge-fund/run-sync` | POST | **Required** | Synchronous analysis |
| `/hedge-fund/run` | POST | **Required** | Streaming analysis |

## 🛡️ Security Implementation

### Authentication Methods

The API supports two authentication methods:

1. **X-API-Key Header**: `X-API-Key: your-api-key`
2. **Bearer Token**: `Authorization: Bearer your-api-key`

### Development vs Production

- **Development**: If no `API_KEY` environment variable is set, authentication is disabled
- **Production**: Authentication is always required for protected endpoints

### Protected vs Public Endpoints

- **Public**: `/`, `/health`, `/hedge-fund/agents`, `/hedge-fund/models`
- **Protected**: `/hedge-fund/run-sync`, `/hedge-fund/run`

## 🚨 Security Best Practices

### API Key Management
- ✅ **Generate strong keys**: Use the provided `generate_api_key.py` script
- ✅ **Environment variables only**: Never hardcode keys in your code
- ✅ **Rotate regularly**: Generate new keys periodically
- ✅ **Monitor usage**: Track API calls and watch for abuse
- ✅ **Restrict access**: Only share keys with authorized users

### Rate Limiting (Recommended)
Consider implementing rate limiting in production:
```python
# Example: Add to FastAPI middleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@limiter.limit("10/minute")
@router.post("/hedge-fund/run-sync")
async def run_hedge_fund_sync(...):
    # Your endpoint code
```

### CORS Configuration
For production, consider restricting CORS origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains only
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 📈 Monitoring & Security

### Railway Dashboard Security
- **Environment Variables**: Ensure all sensitive keys are properly set
- **Logs Monitoring**: Watch for failed authentication attempts
- **Resource Usage**: Monitor for unusual spikes that might indicate abuse

### Authentication Errors
Common HTTP status codes:
- **401 Unauthorized**: Missing or invalid API key
- **403 Forbidden**: Valid key but insufficient permissions (if implemented)
- **429 Too Many Requests**: Rate limit exceeded (if implemented)

### Log Analysis
Monitor logs for patterns like:
```
INFO: "POST /hedge-fund/run-sync HTTP/1.1" 401 Unauthorized
INFO: "POST /hedge-fund/run-sync HTTP/1.1" 200 OK
```

## 🔧 Advanced Security Configuration

### Custom Headers Security
Add security headers to your FastAPI app:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["yourdomain.com", "*.railway.app"]
)
```

### IP Whitelisting (Optional)
For extra security, consider IP whitelisting:
```python
@app.middleware("http")
async def ip_whitelist(request: Request, call_next):
    client_ip = request.client.host
    allowed_ips = ["192.168.1.0/24", "10.0.0.0/8"]  # Your allowed IPs
    # Implementation for IP checking
    response = await call_next(request)
    return response
```

## 🧪 Testing Authentication

### Local Testing Script
```bash
# Test your authentication locally
python test_authenticated_api.py
```

### Production Testing
```bash
# Test public endpoints (should work)
curl https://your-app-name.railway.app/health

# Test protected endpoints without auth (should fail)
curl -X POST "https://your-app-name.railway.app/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{}'

# Test protected endpoints with auth (should work)
curl -X POST "https://your-app-name.railway.app/hedge-fund/run-sync" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["warren_buffett"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI"
  }'
```

## 🚀 Production Security Checklist

- [ ] **API key generated** using secure random method
- [ ] **Environment variables set** in Railway dashboard
- [ ] **Authentication tested** on all protected endpoints
- [ ] **Public endpoints accessible** without authentication
- [ ] **Error messages** don't leak sensitive information
- [ ] **HTTPS enforced** (automatic with Railway)
- [ ] **Monitoring enabled** for failed authentication attempts
- [ ] **API key rotation plan** established
- [ ] **Access logs reviewed** regularly
- [ ] **Rate limiting considered** for high-traffic scenarios

## 💰 Cost & Security Optimization

### Prevent API Abuse
1. **Authentication**: ✅ Implemented
2. **Rate limiting**: Consider implementing
3. **Usage monitoring**: Track costs per API key
4. **Timeout settings**: Prevent long-running requests

### Cost Controls
```bash
# Use cheaper models for testing
"model_name": "gpt-4o-mini"  # Instead of "gpt-4o"

# Limit analysis scope
"tickers": ["AAPL"]  # Instead of ["AAPL", "MSFT", "NVDA", ...]
```

## 🎯 Next Steps

After secure deployment:
1. **Test all authentication methods**
2. **Share API key securely** with authorized users
3. **Monitor usage patterns** and costs
4. **Set up alerts** for unusual activity
5. **Document API usage** for your team
6. **Plan key rotation schedule**

Your AI hedge fund API is now securely deployed with proper authentication! 🔐🚀 