# Railway Deployment Guide

## 🚀 Deploy AI Hedge Fund API to Railway

This guide will help you deploy your AI hedge fund API to Railway for production use.

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **API Keys**: Have your API keys ready for environment variables

## 🛠️ Deployment Steps

### 1. Connect to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your AI hedge fund repository

### 2. Configure Build Settings

Railway will automatically detect the `railway.toml` configuration:
- **Dockerfile**: `Dockerfile.api`
- **Port**: 8000
- **Health Check**: `/health` endpoint

### 3. Set Environment Variables

In your Railway project dashboard, go to **Variables** and add:

#### Required API Keys:
```bash
OPENAI_API_KEY=your-openai-api-key
GROQ_API_KEY=your-groq-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
```

#### Optional Settings:
```bash
PORT=8000
HOST=0.0.0.0
PYTHONUNBUFFERED=1
```

### 4. Deploy

1. Click **"Deploy"** in Railway
2. Wait for the build to complete (2-5 minutes)
3. Your API will be available at: `https://your-app-name.railway.app`

## 🔍 Testing Your Deployed API

### Health Check
```bash
curl https://your-app-name.railway.app/health
```

### List Agents
```bash
curl https://your-app-name.railway.app/hedge-fund/agents
```

### Run Analysis
```bash
curl -X POST "https://your-app-name.railway.app/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["warren_buffett"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI",
    "show_reasoning": true
  }'
```

## 📊 API Endpoints

Your deployed API will have these endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |
| `/hedge-fund/agents` | GET | List available agents |
| `/hedge-fund/models` | GET | List available models |
| `/hedge-fund/run-sync` | POST | Synchronous analysis |
| `/hedge-fund/run` | POST | Streaming analysis |

## 🛡️ Security Considerations

### API Keys Protection
- ✅ Never commit API keys to your repository
- ✅ Use Railway's environment variables
- ✅ Rotate keys regularly

### Rate Limiting
- Consider adding rate limiting for production use
- Monitor usage to prevent abuse
- Set up alerts for unusual activity

## 📈 Monitoring & Scaling

### Railway Dashboard
- **Metrics**: View CPU, memory, and network usage
- **Logs**: Monitor application logs in real-time
- **Deployments**: Track deployment history

### Auto-scaling
Railway automatically scales based on:
- Traffic volume
- Resource usage
- Response times

### Custom Domain (Optional)
1. Go to **Settings** → **Domains**
2. Add your custom domain
3. Configure DNS records as shown

## 🔧 Advanced Configuration

### Custom Resource Limits
Add to your `railway.toml`:
```toml
[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on-failure"
restartPolicyMaxRetries = 3

[resources]
memory = "1GB"
cpu = "1vCPU"
```

### Multiple Environments
```toml
[environments.production]
PORT = "8000"

[environments.staging]
PORT = "8000"
```

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check if Poetry dependencies are correct
   poetry check
   poetry install --dry-run
   ```

2. **Health Check Failures**
   ```bash
   # Test health endpoint locally first
   python app/backend/run_api.py
   curl http://localhost:8000/health
   ```

3. **API Key Errors**
   - Verify all required environment variables are set
   - Check API key validity
   - Ensure keys have proper permissions

4. **Memory Issues**
   - Monitor resource usage in Railway dashboard
   - Consider upgrading to higher memory tier
   - Optimize model selection (use lighter models)

### Logs Access
```bash
# Install Railway CLI
npm install -g @railway/cli

# View logs
railway logs --follow
```

## 💰 Cost Optimization

### Railway Pricing
- **Hobby Plan**: $5/month + usage
- **Pro Plan**: $20/month + usage
- **Team Plan**: $100/month + usage

### Optimization Tips
1. **Use lighter models** (gpt-4o-mini vs gpt-4o)
2. **Optimize Docker image** size
3. **Monitor resource usage** regularly
4. **Set up usage alerts**

## 🚀 Production Checklist

- [ ] All API keys configured in environment variables
- [ ] Health check endpoint working
- [ ] Custom domain configured (optional)
- [ ] Monitoring and alerts set up
- [ ] Rate limiting implemented (recommended)
- [ ] Backup strategy for important data
- [ ] Documentation updated with production URLs

## 📚 Resources

- [Railway Documentation](https://docs.railway.app/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [API Documentation](./app/backend/API_INTERACTION_GUIDE.md)
- [Quick Reference](./app/backend/API_QUICK_REFERENCE.md)

## 🎯 Next Steps

After deployment:
1. Test all endpoints thoroughly
2. Update your frontend/client applications with the new URL
3. Set up monitoring and alerts
4. Share your API documentation with users
5. Consider implementing authentication for production use

Your AI hedge fund API is now live and ready for production use! 🎉 