"""
LangChain Chat Agent for Natural Language Financial Analysis
"""
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser

# Import analysis functions
from src.agents.peter_lynch import (
    analyze_lynch_growth,
    analyze_lynch_fundamentals, 
    analyze_lynch_valuation
)
from src.agents.warren_buffett import (
    analyze_fundamentals,
    analyze_moat,
    analyze_consistency,
    analyze_management_quality
)
from src.agents.aswath_damodaran import (
    analyze_growth_and_reinvestment,
    analyze_risk_profile,
    analyze_relative_valuation
)

# Import data fetching functions
from src.tools.api import (
    get_financial_metrics,
    get_market_cap,
    search_line_items,
    get_prices
)

# Import existing LLM infrastructure
from src.llm.models import get_model

def clean_ticker(ticker: str) -> str:
    """Clean and normalize ticker symbol."""
    return ticker.strip().strip("'\"").upper()

# Define tools for LangChain agent
@tool
def peter_lynch_valuation_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze a stock's valuation using Peter Lynch's approach, focusing on PEG ratio and growth metrics.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing valuation analysis with score, details, and key metrics
    """
    try:
        # Clean ticker (remove quotes if present)
        ticker = clean_ticker(ticker)
        
        # Fetch required data
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        line_items = search_line_items(
            ticker,
            [
                "earnings_per_share", "revenue", "net_income", "outstanding_shares",
                "book_value_per_share", "dividends_and_other_cash_distributions"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        market_cap = get_market_cap(ticker, end_date)
        
        # Run Peter Lynch valuation analysis
        result = analyze_lynch_valuation(line_items, market_cap)
        
        return {
            "ticker": ticker,
            "analysis_type": "peter_lynch_valuation",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "peter_lynch_valuation",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def peter_lynch_growth_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze a stock's growth potential using Peter Lynch's growth investing principles.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing growth analysis with score, details, and key metrics
    """
    try:
        # Clean ticker (remove quotes if present)
        ticker = clean_ticker(ticker)
        
        # Fetch required data
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        line_items = search_line_items(
            ticker,
            ["earnings_per_share", "revenue", "net_income"],
            end_date,
            period="annual", 
            limit=5
        )
        
        # Run Peter Lynch growth analysis
        result = analyze_lynch_growth(line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "peter_lynch_growth",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "peter_lynch_growth", 
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def peter_lynch_fundamentals_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze a stock's fundamental health using Peter Lynch's fundamental analysis approach.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing fundamentals analysis with score, details, and key metrics
    """
    try:
        # Clean ticker (remove quotes if present)
        ticker = clean_ticker(ticker)
        
        # Fetch required data
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        line_items = search_line_items(
            ticker,
            [
                "total_debt", "current_assets", "current_liabilities", 
                "total_assets", "net_income", "revenue"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        # Run Peter Lynch fundamentals analysis
        result = analyze_lynch_fundamentals(line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "peter_lynch_fundamentals",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "peter_lynch_fundamentals",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def warren_buffett_fundamentals_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze a stock using Warren Buffett's fundamental analysis approach.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing Buffett-style analysis with score, details, and key metrics
    """
    try:
        # Clean ticker (remove quotes if present)
        ticker = clean_ticker(ticker)
        
        # Fetch required data
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)
        
        # Run Warren Buffett fundamentals analysis
        result = analyze_fundamentals(metrics)
        
        return {
            "ticker": ticker,
            "analysis_type": "warren_buffett_fundamentals",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "warren_buffett_fundamentals",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

class FinancialAnalysisAgent:
    """LangChain agent for natural language financial analysis."""
    
    def __init__(self, model_name: str = "gpt-4-turbo", model_provider: str = "openai"):
        self.model_name = model_name
        self.model_provider = model_provider
        
        # Initialize LLM using existing infrastructure
        self.llm = get_model(model_name, model_provider)
        if self.llm is None:
            raise ValueError(f"Failed to initialize model: {model_name} with provider: {model_provider}")
        
        # Define available tools
        self.tools = [
            peter_lynch_valuation_analysis,
            peter_lynch_growth_analysis,
            peter_lynch_fundamentals_analysis,
            warren_buffett_fundamentals_analysis
        ]
        
        # Create ReAct agent prompt
        template = """You are an expert financial analyst with access to powerful analysis tools based on legendary investors' methodologies.

Your role is to:
1. Understand natural language queries about stock analysis
2. Identify the ticker symbol, investment style, and analysis type requested
3. Call the appropriate analysis tools to gather data
4. Synthesize the results into clear, actionable insights
5. Provide investment recommendations based on the analysis

Available Analysis Styles:
- Peter Lynch: Growth investing, PEG ratio focus, fundamental analysis
- Warren Buffett: Value investing, moat analysis, quality metrics

When analyzing stocks:
- Always explain your reasoning clearly
- Highlight key metrics and what they mean
- Provide context for scores and ratings
- Give actionable investment insights
- Mention any limitations or risks

For valuation questions, focus on:
- Price-to-earnings ratios
- Growth rates
- PEG ratios (especially for Lynch analysis)
- Comparison to historical averages
- Value vs growth characteristics

IMPORTANT: Format ALL your responses using Markdown formatting. Use the following structure:

## Investment Analysis: [Company Name]

### Analysis Summary
Use **bold** for key metrics and findings.

### Methodology Applied
- **Investment Style**: Peter Lynch/Warren Buffett approach
- **Analysis Type**: Valuation/Growth/Fundamental analysis

### Key Findings
- Use bullet points for main insights
- *Italicize* important financial terms
- **Bold** critical numbers and percentages

### Financial Metrics
Present data in tables when possible:
| Metric | Value | Benchmark | Assessment |
|--------|-------|-----------|------------|
| P/E Ratio | X | Industry avg | High/Low/Fair |

### Investment Recommendation
- **Overall Assessment**: Strong Buy/Buy/Hold/Sell
- **Confidence Level**: X%
- **Key Reasoning**: Provide clear explanation
- **Risk Factors**: List main concerns

Use proper Markdown formatting including ##/### headings, **bold**, *italics*, bullet points (-), and tables (|) to make your analysis clear and professional.

IMPORTANT: When calling tools, pass ONLY the ticker symbol without quotes or extra characters.
For example: Use "TSLA" not "'TSLA'" or "Tesla"

TOOLS:
------
You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        self.prompt = PromptTemplate.from_template(template)
        
        # Create agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    
    async def analyze(self, query: str, chat_history: List = None) -> Dict[str, Any]:
        """
        Process a natural language financial analysis query.
        
        Args:
            query: Natural language query (e.g., "How does Tesla's valuation look from a Peter Lynch perspective?")
            chat_history: Previous conversation messages
            
        Returns:
            Dict containing analysis results and response
        """
        try:
            if chat_history is None:
                chat_history = []
            
            # Run the agent
            result = await self.executor.ainvoke({
                "input": query
            })
            
            return {
                "query": query,
                "response": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "query": query,
                "response": f"I encountered an error while analyzing: {str(e)}",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }

# Lazy initialization to avoid module-level errors
_financial_agent = None

def get_financial_agent():
    """Get or create the financial agent singleton."""
    global _financial_agent
    if _financial_agent is None:
        _financial_agent = FinancialAnalysisAgent()
    return _financial_agent

async def process_financial_query(query: str, chat_history: List = None) -> Dict[str, Any]:
    """
    Process a natural language financial analysis query using the LangChain agent.
    
    Args:
        query: Natural language query
        chat_history: Previous conversation messages
        
    Returns:
        Dict containing analysis results and response
    """
    agent = get_financial_agent()
    return await agent.analyze(query, chat_history) 