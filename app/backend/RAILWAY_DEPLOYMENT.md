# 🚂 Railway Deployment Guide

Deploy your AI Hedge Fund API to Railway with real-time backtesting capabilities.

## 🚀 Quick Deploy

### 1. Connect Repository

1. Go to [Railway](https://railway.app/)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your `ai-hedge-fund` repository

### 2. Configure Environment Variables

Set these environment variables in Railway dashboard:

```bash
# Required
OPENAI_API_KEY=sk-proj-your-openai-key-here

# API Security (recommended for production)
API_KEY=your-secure-api-key-here

# Server Configuration
ENVIRONMENT=production
HOST=0.0.0.0
PORT=8000

# Optional - Additional LLM Providers
ANTHROPIC_API_KEY=your-anthropic-key
DEEPSEEK_API_KEY=your-deepseek-key
GROQ_API_KEY=your-groq-key

# Optional - Financial Data APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
FINANCIAL_MODELING_PREP_API_KEY=your-fmp-key
```

### 3. Set Start Command

In Railway dashboard, set the **Start Command**:

```bash
cd app && python -m backend.run_api
```

### 4. Deploy

Railway will automatically:
- ✅ Install Python dependencies
- ✅ Run your start command
- ✅ Assign a public URL
- ✅ Set up HTTPS

## 🌐 Access Your API

After deployment, your API will be available at:
```
https://your-app-name.railway.app
```

### Test Endpoints:
- **Health Check**: `https://your-app-name.railway.app/health`
- **API Docs**: `https://your-app-name.railway.app/docs`
- **Available Agents**: `https://your-app-name.railway.app/hedge-fund/agents`

## 🔧 Configuration Details

### Environment Variables Explained

| Variable | Purpose | Required |
|----------|---------|----------|
| `OPENAI_API_KEY` | Powers AI analysis | ✅ Yes |
| `API_KEY` | Secures your API | 🔒 Recommended |
| `ENVIRONMENT` | Sets production mode | 🔧 Optional |
| `HOST` | Server bind address | 🔧 Optional |
| `PORT` | Railway assigns this | ⚙️ Auto |

### Security Setup

1. **Generate a secure API key**:
```bash
# Use this Python snippet to generate a secure key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Set the API_KEY environment variable** in Railway

3. **Test authentication**:
```bash
# Without API key (should fail)
curl https://your-app-name.railway.app/backtest/start

# With API key (should work)
curl -H "X-API-Key: your-api-key" \
     https://your-app-name.railway.app/hedge-fund/agents
```

## 📊 Frontend Integration

Update your frontend to use the Railway URL:

```javascript
// Update your base URL
const API_BASE_URL = 'https://your-app-name.railway.app';

// Example: Start a backtest
const response = await fetch(`${API_BASE_URL}/backtest/start`, {
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

// Stream real-time updates
const eventSource = new EventSource(
  `${API_BASE_URL}/backtest/stream/${backtest_id}`,
  {
    headers: {
      'X-API-Key': 'your-api-key'
    }
  }
);
```

## 🔄 CORS Configuration

If your frontend is on a different domain, update CORS settings in `main.py`:

```python
# Update for your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-frontend-domain.com",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📈 Monitoring & Logs

### View Logs
1. Go to Railway dashboard
2. Click on your service
3. Go to **"Deployments"** tab
4. Click **"View Logs"**

### Health Monitoring
```bash
# Check if API is healthy
curl https://your-app-name.railway.app/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-05-29T12:00:00Z",
  "service": "AI Hedge Fund API"
}
```

## 🚨 Troubleshooting

### Common Issues

#### 1. **Build Fails**
```bash
# Check Railway logs for missing dependencies
# Ensure requirements.txt includes all packages
```

#### 2. **Import Errors**
```bash
# Verify start command is: cd app && python -m backend.run_api
# NOT: python app/backend/run_api.py
```

#### 3. **Environment Variables Missing**
```bash
# Check Railway dashboard environment variables
# Ensure OPENAI_API_KEY is set correctly
```

#### 4. **CORS Issues**
```bash
# Update allowed origins in main.py
# Add your frontend domain to allow_origins
```

### Debug Commands

```bash
# Test API locally before deploying
cd app && python -m backend.run_api

# Check environment variables
echo $OPENAI_API_KEY

# Test API endpoints
curl -H "X-API-Key: your-key" https://your-app.railway.app/hedge-fund/agents
```

## 🔒 Security Best Practices

1. **Use strong API keys**: Generate with `secrets.token_urlsafe(32)`
2. **Limit CORS origins**: Don't use `"*"` in production
3. **Monitor usage**: Check Railway metrics for unusual activity
4. **Rotate keys**: Periodically update API keys
5. **Environment separation**: Use different keys for dev/prod

## 📊 Performance Tips

1. **Cold starts**: Railway may have cold starts for serverless plans
2. **Keep alive**: Implement periodic health checks to prevent sleeping
3. **Caching**: Consider Redis for session caching if needed
4. **Monitoring**: Use Railway metrics to track performance

## 💰 Cost Optimization

- **Hobby Plan**: Free tier with limitations
- **Pro Plan**: $5/month per service with better performance
- **Usage-based**: Monitor compute time and resource usage

## 🚀 Advanced Features

### Custom Domain
1. Purchase a domain
2. Add it in Railway dashboard
3. Update DNS records
4. Railway handles SSL automatically

### Database Integration
```bash
# Add PostgreSQL
railway add postgresql

# Environment variable automatically added:
# DATABASE_URL=postgresql://...
```

## 📞 Support

- **Railway Docs**: https://docs.railway.app/
- **Railway Discord**: https://discord.gg/railway
- **API Issues**: Check `/health` endpoint and logs

## 🎯 Next Steps

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Verify real-time streaming works
3. ✅ Update frontend to use Railway URL
4. ✅ Monitor performance and logs
5. ✅ Set up custom domain (optional)

Your AI Hedge Fund API is now live and ready for production use! 🚀 