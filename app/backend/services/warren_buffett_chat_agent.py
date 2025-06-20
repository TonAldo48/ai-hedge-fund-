"""
Warren Buffett Chat Agent for Natural Language Financial Analysis
"""
import os
from typing import Dict, Any, List, AsyncGenerator, Optional
from datetime import datetime, timedelta
import json
import asyncio
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.manager import CallbackManager
from langchain_core.outputs import LLMResult
from langchain.schema import AgentAction, AgentFinish

# Import Warren Buffett analysis functions
from src.agents.warren_buffett import (
    analyze_fundamentals,
    analyze_moat,
    analyze_consistency,
    analyze_management_quality,
    calculate_intrinsic_value,
    calculate_owner_earnings
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

@tool
def warren_buffett_fundamentals_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze a stock's fundamental health using Warren Buffett's criteria.
    Evaluates ROE, debt levels, operating margins, and liquidity position.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing fundamentals analysis with score, details, and key metrics
    """
    try:
        logger.info(f"🔧 TOOL CALL: warren_buffett_fundamentals_analysis for ticker: {ticker}")
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)
        result = analyze_fundamentals(metrics)
        
        logger.info(f"✅ TOOL RESULT: Fundamentals analysis for {ticker} completed with score: {result.get('score', 'N/A')}")
        
        return {
            "ticker": ticker,
            "analysis_type": "warren_buffett_fundamentals",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ TOOL ERROR: warren_buffett_fundamentals_analysis failed for {ticker}: {str(e)}")
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "warren_buffett_fundamentals",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def warren_buffett_moat_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze a company's competitive moat using Buffett's approach.
    Looks for durable competitive advantages through stable ROE and margins.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing moat analysis with score, details, and competitive advantage assessment
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)
        result = analyze_moat(metrics)
        
        return {
            "ticker": ticker,
            "analysis_type": "warren_buffett_moat",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "warren_buffett_moat",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def warren_buffett_consistency_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze earnings consistency and growth using Buffett's criteria.
    Evaluates earnings stability and growth trends over multiple periods.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing consistency analysis with score, details, and earnings trends
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            ["net_income", "revenue", "earnings_per_share"],
            end_date,
            period="annual",
            limit=10
        )
        
        result = analyze_consistency(financial_line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "warren_buffett_consistency",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "warren_buffett_consistency",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def warren_buffett_management_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze management quality using Buffett's shareholder-oriented criteria.
    Evaluates share buybacks, dividends, and capital allocation decisions.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing management analysis with score, details, and shareholder focus assessment
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            [
                "issuance_or_purchase_of_equity_shares",
                "dividends_and_other_cash_distributions",
                "outstanding_shares"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        result = analyze_management_quality(financial_line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "warren_buffett_management",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "warren_buffett_management",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def warren_buffett_intrinsic_value_analysis(ticker: str) -> Dict[str, Any]:
    """
    Calculate intrinsic value using Buffett's DCF approach with owner earnings.
    Provides margin of safety calculation and valuation assessment.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing intrinsic value analysis with valuation, margin of safety, and investment recommendation
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            [
                "net_income", "depreciation_and_amortization", "capital_expenditure",
                "outstanding_shares", "revenue"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        market_cap = get_market_cap(ticker, end_date)
        result = calculate_intrinsic_value(financial_line_items)
        
        # Add margin of safety calculation
        margin_of_safety = None
        if result.get("intrinsic_value") and market_cap:
            margin_of_safety = (result["intrinsic_value"] - market_cap) / market_cap
            result["margin_of_safety"] = margin_of_safety
            result["market_cap"] = market_cap
        
        return {
            "ticker": ticker,
            "analysis_type": "warren_buffett_intrinsic_value",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "warren_buffett_intrinsic_value",
            "error": str(e),
            "result": {"intrinsic_value": None, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def warren_buffett_owner_earnings_analysis(ticker: str) -> Dict[str, Any]:
    """
    Calculate owner earnings using Buffett's preferred earnings measure.
    Owner Earnings = Net Income + Depreciation - Maintenance CapEx
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing owner earnings analysis with components and true earnings power assessment
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            ["net_income", "depreciation_and_amortization", "capital_expenditure"],
            end_date,
            period="annual",
            limit=5
        )
        
        result = calculate_owner_earnings(financial_line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "warren_buffett_owner_earnings",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "warren_buffett_owner_earnings",
            "error": str(e),
            "result": {"owner_earnings": None, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def get_stock_quote(ticker: str) -> Dict[str, Any]:
    """
    Fetch the latest stock quote (price, change, market-cap, etc.) for a ticker symbol.

    Data source: Financial Datasets API (`https://api.financialdatasets.ai`).
    Requires `FINANCIAL_DATASETS_API_KEY` environment variable to be set.  Intended as a
    lightweight grounding tool the agent can call when it needs up-to-the-minute pricing context.
    """
    try:
        ticker_clean = clean_ticker(ticker)
        today = datetime.now().strftime("%Y-%m-%d")

        try:
            from src.tools.api import get_prices  # local helper that already handles caching & auth

            prices = get_prices(ticker_clean, today, today)
            if not prices:
                raise ValueError("No price data returned for today")

            p = prices[0]

            return {
                "ticker": ticker_clean,
                "price": p.close,
                "open": p.open,
                "high": p.high,
                "low": p.low,
                "volume": p.volume,
                "timestamp": p.time,
            }
        except Exception as e:
            raise e
    except Exception as e:
        logger.error(f"get_stock_quote tool error for {ticker}: {e}")
        return {
            "ticker": ticker,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

class StreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler to stream agent decisions and actions."""
    
    def __init__(self, queue: asyncio.Queue, loop: Optional[asyncio.AbstractEventLoop] = None):
        self.queue = queue
        self.current_step = 0
        self.loop = loop
        
    def _send_event_sync(self, event_type: str, data: Dict[str, Any]):
        """Send an event to the streaming queue (thread-safe)."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "step": self.current_step
        }
        
        # If we have a loop, schedule the coroutine
        if self.loop and not self.loop.is_closed():
            try:
                asyncio.run_coroutine_threadsafe(
                    self.queue.put(json.dumps(event)), 
                    self.loop
                )
            except Exception as e:
                # Fallback: just print for debugging
                print(f"📊 {event_type}: {data.get('message', data)}")
        else:
            # Fallback: just print for debugging  
            print(f"📊 {event_type}: {data.get('message', data)}")
    
    def on_agent_action(self, action: AgentAction, **kwargs) -> Any:
        """Called when agent decides to take an action."""
        self._send_event_sync("agent_action", {
            "tool": action.tool,
            "tool_input": action.tool_input,
            "log": action.log,
            "message": f"🔧 Using tool: {action.tool}",
            "details": f"Analyzing {action.tool_input} with {action.tool}"
        })
        
    def on_agent_finish(self, finish: AgentFinish, **kwargs) -> Any:
        """Called when agent finishes."""
        self._send_event_sync("agent_finish", {
            "output": finish.return_values.get("output", ""),
            "message": "✅ Analysis complete",
            "log": finish.log
        })
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> Any:
        """Called when a tool starts."""
        tool_name = serialized.get("name", "Unknown tool")
        self._send_event_sync("tool_start", {
            "tool_name": tool_name,
            "input": input_str,
            "message": f"⚡ Running {tool_name} analysis...",
            "details": f"Fetching data for: {input_str}"
        })
    
    def on_tool_end(self, output: str, **kwargs) -> Any:
        """Called when a tool ends."""
        self._send_event_sync("tool_end", {
            "output": output[:200] + "..." if len(output) > 200 else output,
            "message": "📊 Analysis data received",
            "details": "Processing financial metrics..."
        })
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> Any:
        """Called when LLM starts thinking."""
        self.current_step += 1
        self._send_event_sync("llm_thinking", {
            "message": "🤔 Warren Buffett is thinking...",
            "details": "Analyzing the data and formulating response",
            "step": self.current_step
        })
    
    def on_llm_end(self, response: LLMResult, **kwargs) -> Any:
        """Called when LLM finishes thinking."""
        if response.generations and response.generations[0]:
            content = response.generations[0][0].text
            # Extract the thought process
            if "Thought:" in content:
                thought = content.split("Thought:")[1].split("\n")[0].strip()
                self._send_event_sync("llm_thought", {
                    "thought": thought,
                    "message": f"💭 Thought: {thought}",
                    "details": "Deciding next action..."
                })
    
    def on_text(self, text: str, **kwargs) -> Any:
        """Called when agent produces text."""
        if "Thought:" in text:
            thought = text.split("Thought:")[1].split("\n")[0].strip()
            self._send_event_sync("agent_thinking", {
                "thought": thought,
                "message": f"💭 {thought}",
                "details": "Processing analysis logic..."
            })

class WarrenBuffettChatAgent:
    """Warren Buffett specialized chat agent for value investing analysis."""
    
    def __init__(self, model_name: str = "gpt-4o", model_provider: str = "openai"):
        self.model_name = model_name
        self.model_provider = model_provider
        
        # Initialize LLM using existing infrastructure
        self.llm = get_model(model_name, model_provider)
        if self.llm is None:
            raise ValueError(f"Failed to initialize model: {model_name} with provider: {model_provider}")
        
        # Use the tools defined in this module
        self.tools = [
            warren_buffett_fundamentals_analysis,
            warren_buffett_moat_analysis,
            warren_buffett_consistency_analysis,
            warren_buffett_management_analysis,
            warren_buffett_intrinsic_value_analysis,
            warren_buffett_owner_earnings_analysis,
            get_stock_quote,
        ]
        
        # Create prompt (reuse existing one)
        template = """You are Warren Buffett, the legendary value investor and chairman of Berkshire Hathaway. You are known for your long-term investment philosophy, focus on intrinsic value, and ability to identify companies with strong competitive moats.

Your investment philosophy includes:
- Focus on businesses you can understand
- Look for companies with sustainable competitive advantages (economic moats)
- Buy at prices below intrinsic value (margin of safety)
- Think like an owner, not a trader
- Favor consistent, predictable earnings
- Prefer companies with excellent management
- Be patient and disciplined

When analyzing companies, you consider:
- Business fundamentals (ROE, margins, debt levels)
- Competitive moat strength and durability  
- Earnings consistency and predictability
- Management quality and capital allocation
- Intrinsic value calculation and margin of safety

You should respond in Warren Buffett's characteristic style - folksy, using analogies, referring to business principles, and focusing on long-term value creation.

IMPORTANT: Format ALL your responses using Markdown formatting. Use the following structure:

## Analysis Summary
Use **bold** for key points and metrics.

### Key Strengths
- Use bullet points for strengths
- *Italicize* company names and important terms

### Concerns or Risks  
- Use bullet points for concerns
- **Bold** critical issues

### Financial Metrics
Present key numbers in a table when possible:
| Metric | Value | Assessment |
|--------|-------|------------|
| ROE | X% | Strong/Weak |

### Investment Recommendation
- **Signal**: Bullish/Bearish/Neutral
- **Confidence**: X%
- **Reasoning**: Provide clear explanation

Use proper Markdown headings (##, ###), **bold**, *italics*, bullet points (-), and tables (|) to structure your analysis clearly and professionally.

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
        
        # Create non-streaming agent for regular use
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=8,
            handle_parsing_errors=True
        )
    
    async def analyze(self, query: str, chat_history: List = None) -> Dict[str, Any]:
        """
        Process a natural language financial analysis query with Warren Buffett's perspective.
        
        Args:
            query: Natural language query (e.g., "What do you think about Apple's moat?")
            chat_history: Previous conversation messages
            
        Returns:
            Dict containing analysis results and Buffett-style response
        """
        try:
            logger.info(f"🎯 ANALYZE REQUEST: Received query: '{query}'")
            logger.info(f"📋 CHAT HISTORY: {len(chat_history or [])} previous messages")
            
            # Execute the agent
            logger.info(f"🚀 AGENT EXECUTION: Starting Warren Buffett agent analysis...")
            result = await self.executor.ainvoke({
                "input": query,
                "chat_history": chat_history or []
            })
            
            logger.info(f"✅ AGENT COMPLETE: Analysis finished successfully")
            logger.info(f"📝 RESPONSE LENGTH: {len(result.get('output', ''))}")
            logger.info(f"🔍 INTERMEDIATE STEPS: {len(result.get('intermediate_steps', []))}")
            logger.info(f"📄 RESPONSE PREVIEW: {result.get('output', '')[:100]}...")
            
            return {
                "response": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "agent": "warren_buffett"
            }
            
        except Exception as e:
            logger.error(f"❌ ANALYZE ERROR: {str(e)}")
            logger.exception("Full error traceback:")
            return {
                "response": f"I apologize, but I encountered an error while analyzing your question: {str(e)}",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "agent": "warren_buffett"
            }
        
    async def analyze_streaming(self, query: str, chat_history: List = None) -> AsyncGenerator[str, None]:
        """
        Stream the analysis process in real-time.
        
        Args:
            query: Natural language query
            chat_history: Previous conversation messages
            
        Yields:
            JSON strings containing streaming events
        """
        # Create streaming queue
        stream_queue = asyncio.Queue()
        
        # Get current event loop
        current_loop = asyncio.get_running_loop()
        
        # Create callback handler
        callback_handler = StreamingCallbackHandler(stream_queue, current_loop)
        callback_manager = CallbackManager([callback_handler])
        
        # Create agent with streaming callbacks
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            max_iterations=8,
            handle_parsing_errors=True,
            callbacks=callback_manager
        )
        
        # Start the analysis in background
        analysis_task = asyncio.create_task(
            executor.ainvoke({
                "input": query,
                "chat_history": chat_history or []
            })
        )
        
        # Send initial event
        initial_event = {
            "type": "start",
            "data": {
                "message": "🎯 Starting Warren Buffett analysis...",
                "query": query,
                "agent": "warren_buffett"
            },
            "timestamp": datetime.now().isoformat()
        }
        yield json.dumps(initial_event)
        
        # Stream events until analysis is complete
        while not analysis_task.done():
            try:
                # Wait for streaming events or timeout
                event_json = await asyncio.wait_for(stream_queue.get(), timeout=1.0)
                yield event_json
            except asyncio.TimeoutError:
                # Send heartbeat to keep connection alive
                heartbeat = {
                    "type": "heartbeat",
                    "data": {"message": "Processing..."},
                    "timestamp": datetime.now().isoformat()
                }
                yield json.dumps(heartbeat)
        
        # Get final result
        try:
            result = await analysis_task
            final_event = {
                "type": "complete",
                "data": {
                    "response": result["output"],
                    "success": True,
                    "agent": "warren_buffett"
                },
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(final_event)
        except Exception as e:
            error_event = {
                "type": "error",
                "data": {
                    "error": str(e),
                    "success": False,
                    "agent": "warren_buffett"
                },
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(error_event)

# Global agent instance with lazy initialization
_warren_buffett_agent = None

def get_warren_buffett_agent():
    """Get or create the Warren Buffett chat agent instance."""
    global _warren_buffett_agent
    if _warren_buffett_agent is None:
        _warren_buffett_agent = WarrenBuffettChatAgent()
    return _warren_buffett_agent

async def process_warren_buffett_query(query: str, chat_history: List = None) -> Dict[str, Any]:
    """
    Process a natural language query using Warren Buffett's investment approach.
    
    Args:
        query: Natural language query about stocks or investing
        chat_history: Previous conversation messages
        
    Returns:
        Dict containing Warren Buffett's analysis and response
    """
    agent = get_warren_buffett_agent()
    return await agent.analyze(query, chat_history) 