# AI Hedge Fund

This is a proof of concept for an AI-powered hedge fund.  The goal of this project is to explore the use of AI to make trading decisions.  This project is for **educational** purposes only and is not intended for real trading or investment.

This system employs several agents working together:

1. Aswath Damodaran Agent - The Dean of Valuation, focuses on story, numbers, and disciplined valuation
2. Ben Graham Agent - The godfather of value investing, only buys hidden gems with a margin of safety
3. Bill Ackman Agent - An activist investor, takes bold positions and pushes for change
4. Cathie Wood Agent - The queen of growth investing, believes in the power of innovation and disruption
5. Charlie Munger Agent - Warren Buffett's partner, only buys wonderful businesses at fair prices
6. Michael Burry Agent - The Big Short contrarian who hunts for deep value
7. Peter Lynch Agent - Practical investor who seeks "ten-baggers" in everyday businesses
8. Phil Fisher Agent - Meticulous growth investor who uses deep "scuttlebutt" research 
9. Stanley Druckenmiller Agent - Macro legend who hunts for asymmetric opportunities with growth potential
10. Warren Buffett Agent - The oracle of Omaha, seeks wonderful companies at a fair price
11. Valuation Agent - Calculates the intrinsic value of a stock and generates trading signals
12. Sentiment Agent - Analyzes market sentiment and generates trading signals
13. Fundamentals Agent - Analyzes fundamental data and generates trading signals
14. Technicals Agent - Analyzes technical indicators and generates trading signals
15. Risk Manager - Calculates risk metrics and sets position limits
16. Portfolio Manager - Makes final trading decisions and generates orders
    
<img width="1042" alt="Screenshot 2025-03-22 at 6 19 07 PM" src="https://github.com/user-attachments/assets/cbae3dcf-b571-490d-b0ad-3f0f035ac0d4" />


**Note**: the system simulates trading decisions, it does not actually trade.

[![Twitter Follow](https://img.shields.io/twitter/follow/virattt?style=social)](https://twitter.com/virattt)

## Disclaimer

This project is for **educational and research purposes only**.

- Not intended for real trading or investment
- No investment advice or guarantees provided
- Creator assumes no liability for financial losses
- Consult a financial advisor for investment decisions
- Past performance does not indicate future results

By using this software, you agree to use it solely for learning purposes.

## Table of Contents
- [Setup](#setup)
  - [Using Poetry](#using-poetry)
  - [Using Docker](#using-docker)
- [Usage](#usage)
  - [Running the Hedge Fund](#running-the-hedge-fund)
  - [Running the Backtester](#running-the-backtester)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Feature Requests](#feature-requests)
- [License](#license)

## Setup

### Using Poetry

Clone the repository:
```bash
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund
```

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
poetry install
```

3. Set up your environment variables:
```bash
# Create .env file for your API keys
cp .env.example .env
```

4. Set your API keys:
```bash
# For running LLMs hosted by openai (gpt-4o, gpt-4o-mini, etc.)
# Get your OpenAI API key from https://platform.openai.com/
OPENAI_API_KEY=your-openai-api-key

# For running LLMs hosted by groq (deepseek, llama3, etc.)
# Get your Groq API key from https://groq.com/
GROQ_API_KEY=your-groq-api-key

# For getting financial data to power the hedge fund
# Get your Financial Datasets API key from https://financialdatasets.ai/
FINANCIAL_DATASETS_API_KEY=your-financial-datasets-api-key
```

### Using Docker

1. Make sure you have Docker installed on your system. If not, you can download it from [Docker's official website](https://www.docker.com/get-started).

2. Clone the repository:
```bash
git clone https://github.com/virattt/ai-hedge-fund.git
cd ai-hedge-fund
```

3. Set up your environment variables:
```bash
# Create .env file for your API keys
cp .env.example .env
```

4. Edit the .env file to add your API keys as described above.

5. Build the Docker image:
```bash
# On Linux/Mac:
./run.sh build

# On Windows:
run.bat build
```

**Important**: You must set `OPENAI_API_KEY`, `GROQ_API_KEY`, `ANTHROPIC_API_KEY`, or `DEEPSEEK_API_KEY` for the hedge fund to work.  If you want to use LLMs from all providers, you will need to set all API keys.

Financial data for AAPL, GOOGL, MSFT, NVDA, and TSLA is free and does not require an API key.

For any other ticker, you will need to set the `FINANCIAL_DATASETS_API_KEY` in the .env file.

## Usage

### Running the Hedge Fund

#### With Poetry
```bash
poetry run python src/main.py --ticker AAPL,MSFT,NVDA
```

#### With Docker
```bash
# On Linux/Mac:
./run.sh --ticker AAPL,MSFT,NVDA main

# On Windows:
run.bat --ticker AAPL,MSFT,NVDA main
```

**Example Output:**
<img width="992" alt="Screenshot 2025-01-06 at 5 50 17 PM" src="https://github.com/user-attachments/assets/e8ca04bf-9989-4a7d-a8b4-34e04666663b" />

You can also specify a `--ollama` flag to run the AI hedge fund using local LLMs.

```bash
# With Poetry:
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --ollama

# With Docker (on Linux/Mac):
./run.sh --ticker AAPL,MSFT,NVDA --ollama main

# With Docker (on Windows):
run.bat --ticker AAPL,MSFT,NVDA --ollama main
```

You can also specify a `--show-reasoning` flag to print the reasoning of each agent to the console.

```bash
# With Poetry:
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --show-reasoning

# With Docker (on Linux/Mac):
./run.sh --ticker AAPL,MSFT,NVDA --show-reasoning main

# With Docker (on Windows):
run.bat --ticker AAPL,MSFT,NVDA --show-reasoning main
```

You can optionally specify the start and end dates to make decisions for a specific time period.

```bash
# With Poetry:
poetry run python src/main.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-02-01 --show-reasoning

# With Docker (on Linux/Mac):
./run.sh --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 main

# With Docker (on Windows):
run.bat --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 main
```

### Running the Backtester

#### With Poetry
```bash
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA
```

#### With Docker
```bash
# On Linux/Mac:
./run.sh --ticker AAPL,MSFT,NVDA backtest

# On Windows:
run.bat --ticker AAPL,MSFT,NVDA backtest
```

**Example Output:**
<img width="941" alt="Screenshot 2025-01-06 at 5 47 52 PM" src="https://github.com/user-attachments/assets/00e794ea-8628-44e6-9a84-8f8a31ad3b47" />


You can optionally specify the start and end dates to backtest over a specific time period.

```bash
# With Poetry:
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01

# With Docker (on Linux/Mac):
./run.sh --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 backtest

# With Docker (on Windows):
run.bat --ticker AAPL,MSFT,NVDA --start-date 2024-01-01 --end-date 2024-03-01 backtest
```

You can also specify a `--ollama` flag to run the backtester using local LLMs.
```bash
# With Poetry:
poetry run python src/backtester.py --ticker AAPL,MSFT,NVDA --ollama

# With Docker (on Linux/Mac):
./run.sh --ticker AAPL,MSFT,NVDA --ollama backtest

# With Docker (on Windows):
run.bat --ticker AAPL,MSFT,NVDA --ollama backtest
```

### Running the Web API (NEW!)

The hedge fund also includes a modern REST API with real-time streaming capabilities, making it easy to integrate with web applications, mobile apps, or other services.

#### Start the API Server
```bash
# With Poetry:
poetry run python app/backend/run_api.py

# API will be available at: http://localhost:8000
# Interactive docs: https://aeeroooo-production.up.railway.app/docs
```

#### Key API Features
- **RESTful endpoints** for all hedge fund functionality
- **Real-time streaming** with Server-Sent Events
- **Multiple AI agents** (Warren Buffett, Peter Lynch, Technical Analyst, etc.)
- **Show reasoning flag** (equivalent to CLI `--show-reasoning`)
- **Comprehensive documentation** with examples

#### Quick API Examples

**Health Check:**
```bash
curl https://aeeroooo-production.up.railway.app/health
```

**List Available Agents:**
```bash
curl https://aeeroooo-production.up.railway.app/hedge-fund/agents
```

**Run Analysis with Reasoning:**
```bash
curl -X POST "https://aeeroooo-production.up.railway.app/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["warren_buffett"],
    "model_name": "gpt-4o-mini", 
    "model_provider": "OpenAI",
    "show_reasoning": true
  }'
```

**Stream Real-time Analysis:**
```bash
curl -X POST "https://aeeroooo-production.up.railway.app/hedge-fund/run" \
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

#### API Documentation
- **Full API Guide**: `app/backend/API_INTERACTION_GUIDE.md`
- **Quick Reference**: `app/backend/API_QUICK_REFERENCE.md`
- **Postman Collection**: `app/backend/postman_collection.json`
- **Python Test Scripts**: `app/backend/test_*.py`

The API transforms the command-line interface into modern HTTP endpoints while preserving all functionality, including the `show_reasoning` flag for detailed AI explanations.

### 🚀 Deploy to Railway (Production)

Want to deploy your API to the cloud? Railway makes it easy! Your hedge fund API can be live in minutes.

#### Quick Deployment
1. **Sign up** at [railway.app](https://railway.app)
2. **Connect your GitHub repository**
3. **Set environment variables** (API keys)
4. **Deploy!** ✨

#### Deployment Files Included
- `Dockerfile.api` - Production-optimized container
- `railway.toml` - Railway configuration
- `RAILWAY_DEPLOYMENT.md` - Complete deployment guide

#### One-Click Setup
```bash
# Run the deployment helper
./deploy_railway.sh
```

#### After Deployment
Your API will be available at:
- **API**: `https://your-app-name.railway.app`
- **Health Check**: `https://your-app-name.railway.app/health`
- **Documentation**: `https://your-app-name.railway.app/docs`

**Example Production Usage:**
```bash
curl -X POST "https://your-app-name.railway.app/hedge-fund/run-sync" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL"],
    "selected_agents": ["warren_buffett"],
    "model_name": "gpt-4o-mini",
    "model_provider": "OpenAI"
  }'
```

See the complete [Railway Deployment Guide](./RAILWAY_DEPLOYMENT.md) for detailed instructions, security setup, monitoring, and troubleshooting.

## Project Structure 
```
ai-hedge-fund/
├── src/
│   ├── agents/                   # Agent definitions and workflow
│   │   ├── bill_ackman.py        # Bill Ackman agent
│   │   ├── fundamentals.py       # Fundamental analysis agent
│   │   ├── portfolio_manager.py  # Portfolio management agent
│   │   ├── risk_manager.py       # Risk management agent
│   │   ├── sentiment.py          # Sentiment analysis agent
│   │   ├── technicals.py         # Technical analysis agent
│   │   ├── valuation.py          # Valuation analysis agent
│   │   ├── ...                   # Other agents
│   │   ├── warren_buffett.py     # Warren Buffett agent
│   │   ├── aswath_damodaran.py   # Aswath Damodaran agent
│   │   ├── ...                   # Other agents
│   │   ├── ...                   # Other agents
│   ├── tools/                    # Agent tools
│   │   ├── api.py                # API tools
│   ├── backtester.py             # Backtesting tools
│   ├── main.py # Main entry point
├── pyproject.toml
├── ...
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

**Important**: Please keep your pull requests small and focused.  This will make it easier to review and merge.

## Feature Requests

If you have a feature request, please open an [issue](https://github.com/virattt/ai-hedge-fund/issues) and make sure it is tagged with `enhancement`.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
