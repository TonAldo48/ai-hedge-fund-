# 🔍 LangSmith Tracing for AI Hedge Fund

This guide explains how to set up and use LangSmith tracing for monitoring and evaluating your AI hedge fund agents, starting with the Warren Buffett agent.

## 🚀 What is LangSmith Tracing?

LangSmith provides comprehensive observability for your LLM applications. With tracing enabled, you can:

- **See every prompt and response** sent to/from your LLMs
- **Monitor performance** (latency, token usage, costs)
- **Debug agent decisions** by seeing the exact reasoning paths
- **Evaluate prompt effectiveness** with A/B testing
- **Track agent performance** over time
- **Identify optimization opportunities**

## 📋 Prerequisites

1. **LangSmith Account**: Sign up at [smith.langchain.com](https://smith.langchain.com)
2. **API Key**: Get your LangSmith API key from your account settings
3. **LLM Provider Keys**: OpenAI, Anthropic, or other provider API keys

## ⚙️ Setup Instructions

### 1. Configure Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# LangSmith Tracing Configuration (REQUIRED)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=ai-hedge-fund-production

# Environment-specific projects (optional)
LANGSMITH_PROJECT_DEV=ai-hedge-fund-dev
LANGSMITH_PROJECT_STAGING=ai-hedge-fund-staging
LANGSMITH_PROJECT_PRODUCTION=ai-hedge-fund-production

# LLM Provider Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# ... other provider keys as needed

# Application Configuration
ENVIRONMENT=development
```

### 2. Install Dependencies

The required dependencies are already included in your `pyproject.toml`:

```bash
poetry install
```

### 3. Test the Setup

Run the test script to verify tracing is working:

```bash
python test_warren_buffett_tracing.py
```

This will:
- Set up LangSmith tracing
- Run a Warren Buffett analysis on AAPL
- Show you where to find the traces in the LangSmith dashboard

## 🔍 What Gets Traced

### For the Warren Buffett Agent

When you run the Warren Buffett agent with tracing enabled, LangSmith captures:

#### 1. **Main Agent Execution** (`warren_buffett_agent`)
- Input: Stock tickers, dates, model configuration
- Output: Investment signals with confidence and reasoning
- Tags: `hedge_fund`, `value_investing`, `buffett`, `fundamental_analysis`

#### 2. **Analysis Functions**
Each analysis function is individually traced:

- **`analyze_fundamentals`**: ROE, debt ratios, operating margins
- **`analyze_consistency`**: Earnings stability over time  
- **`analyze_moat`**: Competitive advantages analysis
- **`analyze_management_quality`**: Share buybacks, dividends
- **`calculate_intrinsic_value`**: DCF valuation with owner earnings

#### 3. **LLM Calls** (`llm_call`)
- **Input**: The exact formatted prompt sent to the model
- **Output**: The structured response (signal, confidence, reasoning)
- **Metadata**: Model name, provider, token usage, cost, latency

#### 4. **Individual Stock Analysis**
For each ticker analyzed:
- Complete financial data inputs
- Intermediate analysis results
- Final investment decision with reasoning

## 📊 Viewing Traces in LangSmith

### 1. Access Your Dashboard
Visit [smith.langchain.com](https://smith.langchain.com) and navigate to your project.

### 2. Understanding the Trace View

Each Warren Buffett analysis will show up as a trace with:

- **Root Span**: `warren_buffett_agent` - The main agent execution
- **Child Spans**: Each analysis function (`analyze_fundamentals`, etc.)
- **LLM Spans**: The actual model calls with prompts and responses

### 3. Key Information Available

For each trace, you can see:

#### Input Data
```json
{
  "tickers": ["AAPL"],
  "end_date": "2024-01-15",
  "model_name": "gpt-4o-mini",
  "session_id": "session_20240115_143022"
}
```

#### Exact Prompts
```
You are a Warren Buffett AI agent. Decide on investment signals based on Warren Buffett's principles:
- Circle of Competence: Only invest in businesses you understand
- Margin of Safety (> 30%): Buy at a significant discount to intrinsic value
...

Based on the following data, create the investment signal as Warren Buffett would:

Analysis Data for AAPL:
{
  "signal": "bullish",
  "score": 8.2,
  "fundamental_analysis": {
    "score": 6,
    "details": "Strong ROE of 28.5%; Conservative debt levels; Strong operating margins"
  },
  ...
}
```

#### Model Responses
```json
{
  "signal": "bullish",
  "confidence": 85.0,
  "reasoning": "I'm particularly impressed with Apple's exceptional return on equity of 28.5%, reminiscent of our early investment in See's Candies where we saw similar strong profitability metrics..."
}
```

## 🧪 Prompt Evaluation and Optimization

### A/B Testing Prompts

You can test different prompt versions by modifying the system prompt in `generate_buffett_output()`:

1. **Current Prompt**: The existing Warren Buffett persona prompt
2. **Alternative Prompt**: A more quantitative or qualitative version
3. **Compare Results**: Use LangSmith to compare outputs side-by-side

### Evaluation Metrics

Track these metrics in LangSmith:

- **Signal Accuracy**: How often does the agent's signal match expected outcomes?
- **Confidence Calibration**: Are high-confidence predictions more accurate?
- **Reasoning Quality**: How detailed and relevant is the explanation?
- **Consistency**: Does the agent give consistent signals for similar inputs?

## 📈 Monitoring and Alerts

### Performance Metrics

Monitor these key metrics in LangSmith:

- **Latency**: How long each analysis takes
- **Token Usage**: Input/output tokens per analysis
- **Cost**: LLM API costs per ticker analyzed
- **Error Rate**: Failed analyses or LLM calls
- **Success Rate**: Completed analyses

### Custom Monitoring

The tracing system logs additional metadata:

```python
{
  "agent_name": "warren_buffett",
  "ticker": "AAPL", 
  "total_score": 8.2,
  "margin_of_safety": 0.35,
  "intrinsic_value": 185.50,
  "market_cap": 2800000000000
}
```

## 🔧 Advanced Configuration

### Environment-Specific Projects

Use different LangSmith projects for different environments:

```bash
# Development
ENVIRONMENT=development
LANGCHAIN_PROJECT=ai-hedge-fund-dev

# Production  
ENVIRONMENT=production
LANGCHAIN_PROJECT=ai-hedge-fund-production
```

### Custom Tags and Metadata

Add custom tags to traces for better filtering:

```python
@traceable(
    tags=["custom_strategy", "earnings_season", "high_volatility"]
)
def custom_analysis():
    # Your analysis code
    pass
```

### Sampling

For high-volume production use, you can sample traces:

```python
# In your .env file
LANGCHAIN_TRACING_SAMPLING_RATE=0.1  # Trace 10% of requests
```

## 🚨 Troubleshooting

### Common Issues

1. **"LangSmith tracing is not enabled"**
   - Check that `LANGCHAIN_TRACING_V2=true`
   - Verify `LANGCHAIN_API_KEY` is set correctly

2. **"Failed to initialize LangSmith client"**
   - Check your API key is valid
   - Ensure you have network access to smith.langchain.com

3. **Traces not appearing**
   - Check the correct project name
   - Verify the environment variable `LANGCHAIN_PROJECT`

4. **High costs**
   - Monitor token usage in LangSmith
   - Consider using smaller models for development
   - Implement sampling for production

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
ENVIRONMENT=development  # Enables verbose logging
```

## 🎯 Next Steps

1. **Test the setup** with the provided test script
2. **Run actual analyses** with tracing enabled
3. **Explore the LangSmith dashboard** to understand your agent's behavior
4. **Set up evaluation datasets** for systematic prompt testing
5. **Monitor performance** and optimize based on insights
6. **Extend tracing** to other agents (Charlie Munger, Michael Burry, etc.)

## 📚 Additional Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangChain Tracing Guide](https://python.langchain.com/docs/langsmith/tracing)
- [Prompt Engineering Best Practices](https://docs.smith.langchain.com/evaluation/concepts#prompt-engineering)

---

**Happy tracing! 🚀** Your Warren Buffett agent is now fully instrumented for observability and optimization. 