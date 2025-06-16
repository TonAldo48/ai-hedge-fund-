# AI Hedge Fund - System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  USER INTERFACE LAYER                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  CLI Input: --ticker AAPL,MSFT --start-date --end-date --show-reasoning --ollama        │
│  Interactive Selection: Analysts, LLM Models, Portfolio Settings                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              LANGGRAPH WORKFLOW ORCHESTRATOR                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                    [START NODE]                                         │
│                                         │                                               │
│                        ┌────────────────┼────────────────┐                              │
│                        ▼                ▼                ▼                              │
│                          [PARALLEL AGENT EXECUTION LAYER]                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 AGENT LAYER (16 AGENTS)                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │   FAMOUS INVESTORS  │  │  ANALYTICAL AGENTS  │  │  MANAGEMENT AGENTS  │              │
│  │    (10 Agents)      │  │     (4 Agents)      │  │     (2 Agents)      │              │
│  ├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤              │
│  │ • Warren Buffett    │  │ • Technical Analyst │  │ • Risk Manager      │              │
│  │ • Charlie Munger    │  │ • Fundamentals      │  │ • Portfolio Manager │              │
│  │ • Peter Lynch       │  │ • Sentiment         │  └─────────────────────┘              │
│  │ • Ben Graham        │  │ • Valuation         │                                       │
│  │ • Michael Burry     │  └─────────────────────┘                                       │
│  │ • Bill Ackman       │                                                                │
│  │ • Cathie Wood       │                                                                │
│  │ • Phil Fisher       │                                                                │
│  │ • Stanley Druckenmil│                                                                │
│  │ • Aswath Damodaran  │                                                                │
│  └─────────────────────┘                                                                │
│                                                                                         │
│  Flow: All agents run in PARALLEL → Generate individual signals & recommendations       │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                AGGREGATION & DECISION                                   │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  All Agent Signals → [RISK MANAGER] → [PORTFOLIO MANAGER] → Final Trading Decisions     │
│                           │                    │                                        │
│                           ▼                    ▼                                        │
│                    • Position Limits    • Aggregates all signals                        │
│                    • Risk Metrics       • Weighs recommendations                        │
│                    • Exposure Limits    • Generates BUY/SELL/HOLD                       │
│                                         • Sets position sizes                           │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    DATA LAYER                                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ PRICE DATA      │  │ FINANCIAL       │  │ NEWS & SENTIMENT│  │ INSIDER TRADES  │     │
│  │ • OHLCV         │  │ METRICS         │  │ • Company News  │  │ • Transactions  │     │
│  │ • Historical    │  │ • P/E, ROE      │  │ • Market Sent.  │  │ • Filing Dates  │     │
│  │ • Real-time     │  │ • Revenue       │  │ • Social Media  │  │ • Trade Values  │     │
│  └─────────────────┘  │ • Earnings      │  └─────────────────┘  └─────────────────┘     │
│                       │ • Cash Flow     │                                               │
│                       └─────────────────┘                                               │
│                                                                                         │
│  Data Sources: Financial Datasets API + Local Cache                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  LLM PROVIDER LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ OPENAI          │  │ GROQ            │  │ ANTHROPIC       │  │ OLLAMA (LOCAL)  │     │
│  │ • GPT-4o        │  │ • Deepseek      │  │ • Claude        │  │ • Llama3        │     │
│  │ • GPT-4o-mini   │  │ • Llama3        │  │ • Sonnet        │  │ • Mistral       │     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │ • Gemma         │     │
│                                                                 └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                               INFRASTRUCTURE LAYER                                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │
│  │ DOCKER          │  │ DOCKER COMPOSE  │  │ RAILWAY         │  │ POETRY          │     │
│  │ • Containerized │  │ • Multi-service │  │ • Cloud Deploy  │  │ • Dependencies  │     │
│  │ • Reproducible  │  │ • Ollama + App  │  │ • Auto-scaling  │  │ • Env Management│     │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## State Management Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                  AGENT STATE                                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐                         │
│  │   MESSAGES      │  │      DATA        │  │    METADATA     │                         │
│  │ • User queries  │  │ • Tickers        │  │ • Model name    │                         │
│  │ • Agent responses│ │ • Portfolio      │  │ • Show reasoning│                         │
│  │ • Trading signals│ │ • Start/End date │  │ • Provider info │                         │
│  │ • Final decisions│ │ • Analyst signals│  │ • Timestamps    │                         │
│  └─────────────────┘  └──────────────────┘  └─────────────────┘                         │
│                                                                                         │
│  State flows through: Start → Agents (parallel) → Risk → Portfolio → End                │
│  Each agent adds their analysis to the shared state                                     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Execution Flow

```
1. USER INPUT
   ├── Tickers: AAPL,MSFT,NVDA
   ├── Date Range: 2024-01-01 to 2024-12-31
   ├── Analyst Selection: Interactive checkbox
   └── Model Selection: GPT-4o, Groq, etc.

2. DATA GATHERING
   ├── Price History → Financial Datasets API
   ├── Financial Metrics → Cached/API
   ├── News & Sentiment → External APIs
   └── Market Data → Real-time feeds

3. PARALLEL AGENT ANALYSIS
   ├── Warren Buffett → "Quality at fair price" signal
   ├── Technical Analyst → RSI, MACD, trends
   ├── Sentiment Analyst → News sentiment score
   └── 13 other agents → Individual recommendations

4. RISK MANAGEMENT
   ├── Aggregate all 16 agent signals
   ├── Calculate position limits
   ├── Apply risk constraints
   └── Generate risk-adjusted signals

5. PORTFOLIO DECISIONS
   ├── Weight agent recommendations
   ├── Consider portfolio balance
   ├── Generate BUY/SELL/HOLD decisions
   └── Set position sizes

6. OUTPUT
   ├── Trading decisions (JSON)
   ├── Individual agent reasoning (optional)
   ├── Risk metrics
   └── Portfolio changes
```

## Key Design Patterns

- **Multi-Agent Orchestration**: LangGraph manages parallel agent execution
- **State Management**: Shared state object flows through all agents
- **Modular Architecture**: Each agent is independent and pluggable
- **Caching Strategy**: Financial data cached locally to reduce API calls
- **Provider Abstraction**: Support for multiple LLM providers
- **Containerized Deployment**: Docker for reproducible environments

## Agent Personalities & Strategies

### Famous Investor Agents (10)
- **Warren Buffett**: Seeks wonderful companies at fair prices, long-term value
- **Charlie Munger**: Quality businesses with durable competitive advantages
- **Peter Lynch**: Practical investor seeking "ten-baggers" in everyday businesses
- **Ben Graham**: Value investing with margin of safety, hidden gems
- **Michael Burry**: Contrarian deep value investor, "Big Short" mentality
- **Bill Ackman**: Activist investor, takes bold positions and pushes for change
- **Cathie Wood**: Growth investing, believes in innovation and disruption
- **Phil Fisher**: Meticulous growth investor using deep "scuttlebutt" research
- **Stanley Druckenmiller**: Macro legend hunting asymmetric opportunities
- **Aswath Damodaran**: Dean of Valuation, focuses on story, numbers, disciplined 
  valuation

### Analytical Agents (4)
- **Technical Analyst**: Chart patterns, RSI, MACD, moving averages, trend analysis
- **Fundamentals Analyst**: P/E ratios, revenue growth, earnings, cash flow analysis
- **Sentiment Analyst**: Market sentiment, news analysis, social media trends
- **Valuation Analyst**: DCF models, intrinsic value calculations, fair value estimates

### Management Agents (2)
- **Risk Manager**: Position limits, portfolio risk metrics, exposure controls
- **Portfolio Manager**: Final trading decisions, position sizing, order generation

## Technology Stack

```
Frontend:        Command Line Interface (CLI)
Orchestration:   LangGraph (StateGraph workflow management)
Agents:          LangChain-based AI agents with distinct personalities
LLM Providers:   OpenAI, Groq, Anthropic, Ollama (local)
Data Sources:    Financial Datasets API, cached financial data
Infrastructure:  Docker, Docker Compose, Railway (deployment)
Dependencies:    Poetry (Python package management)
Languages:       Python 3.x
```

## Data Sources & APIs

```
Primary Data:    Financial Datasets API
Price Data:      OHLCV historical and real-time
Fundamentals:    P/E, ROE, revenue, earnings, cash flow
News:            Company news, market sentiment
Insider Trading: Transaction data, filing information
Market Cap:      Real-time market capitalization
Caching:         Local cache for API optimization
```

This architecture enables sophisticated multi-agent investment decision-making by 
combining diverse investment philosophies, real-time data analysis, and robust risk 
management in a scalable, containerized system. 