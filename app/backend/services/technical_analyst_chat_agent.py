"""
Technical Analyst Chat Agent for Natural Language Financial Analysis
"""
import os
from typing import Dict, Any, List, AsyncGenerator, Optional
from datetime import datetime, timedelta
import json
import asyncio
import pandas as pd
import numpy as np

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

# Import Technical analysis functions
from src.agents.technicals import (
    calculate_trend_signals,
    calculate_mean_reversion_signals,
    calculate_momentum_signals,
    calculate_volatility_signals,
    calculate_stat_arb_signals,
    prices_to_df
)

# Import data fetching functions
from src.tools.api import (
    get_prices,
    get_market_cap
)

# Import existing LLM infrastructure
from src.llm.models import get_model

def clean_ticker(ticker: str) -> str:
    """Clean and normalize ticker symbol."""
    return ticker.strip().strip("'\"").upper()

@tool
def technical_trend_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze trend following signals using moving averages and ADX.
    Identifies trend direction, strength, and potential entry/exit points.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing trend analysis with signals and confidence levels
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # Get 1 year of data for technical analysis
        
        prices = get_prices(
            ticker, 
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        # Convert to DataFrame
        prices_df = prices_to_df(prices)
        
        # Calculate trend signals
        result = calculate_trend_signals(prices_df)
        
        return {
            "ticker": ticker,
            "analysis_type": "technical_trend",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "technical_trend",
            "error": str(e),
            "result": {"signal": "neutral", "confidence": 0, "metrics": {}, "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }

@tool
def technical_momentum_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze momentum indicators including RSI, MACD, and rate of change.
    Identifies overbought/oversold conditions and momentum shifts.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing momentum analysis with buy/sell signals
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        prices = get_prices(
            ticker, 
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        # Convert to DataFrame
        prices_df = prices_to_df(prices)
        
        # Calculate momentum signals
        result = calculate_momentum_signals(prices_df)
        
        return {
            "ticker": ticker,
            "analysis_type": "technical_momentum",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "technical_momentum",
            "error": str(e),
            "result": {"signal": "neutral", "confidence": 0, "metrics": {}, "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }

@tool
def technical_mean_reversion_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze mean reversion opportunities using Bollinger Bands and z-scores.
    Identifies when price deviates significantly from historical norms.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing mean reversion signals and statistical metrics
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        prices = get_prices(
            ticker, 
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        # Convert to DataFrame
        prices_df = prices_to_df(prices)
        
        # Calculate mean reversion signals
        result = calculate_mean_reversion_signals(prices_df)
        
        return {
            "ticker": ticker,
            "analysis_type": "technical_mean_reversion",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "technical_mean_reversion",
            "error": str(e),
            "result": {"signal": "neutral", "confidence": 0, "metrics": {}, "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }

@tool
def technical_volatility_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze volatility patterns using ATR, historical volatility, and regime detection.
    Identifies volatility expansions/contractions and trading opportunities.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing volatility analysis and regime identification
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        prices = get_prices(
            ticker, 
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        # Convert to DataFrame
        prices_df = prices_to_df(prices)
        
        # Calculate volatility signals
        result = calculate_volatility_signals(prices_df)
        
        return {
            "ticker": ticker,
            "analysis_type": "technical_volatility",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "technical_volatility",
            "error": str(e),
            "result": {"signal": "neutral", "confidence": 0, "metrics": {}, "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }

@tool
def technical_support_resistance_analysis(ticker: str) -> Dict[str, Any]:
    """
    Identify key support and resistance levels using price action and volume.
    Helps determine entry/exit points and stop-loss levels.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing support/resistance levels and price targets
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        prices = get_prices(
            ticker, 
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        
        # Convert to DataFrame
        prices_df = prices_to_df(prices)
        
        # Calculate key levels
        current_price = prices_df['close'].iloc[-1]
        high_52w = prices_df['high'].max()
        low_52w = prices_df['low'].min()
        
        # Calculate pivots
        pivot = (prices_df['high'].iloc[-1] + prices_df['low'].iloc[-1] + prices_df['close'].iloc[-1]) / 3
        r1 = 2 * pivot - prices_df['low'].iloc[-1]
        s1 = 2 * pivot - prices_df['high'].iloc[-1]
        r2 = pivot + (prices_df['high'].iloc[-1] - prices_df['low'].iloc[-1])
        s2 = pivot - (prices_df['high'].iloc[-1] - prices_df['low'].iloc[-1])
        
        result = {
            "current_price": float(current_price),
            "52_week_high": float(high_52w),
            "52_week_low": float(low_52w),
            "pivot_point": float(pivot),
            "resistance_1": float(r1),
            "resistance_2": float(r2),
            "support_1": float(s1),
            "support_2": float(s2),
            "price_position": "Near resistance" if current_price > r1 else "Near support" if current_price < s1 else "Mid-range"
        }
        
        return {
            "ticker": ticker,
            "analysis_type": "technical_support_resistance",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "technical_support_resistance",
            "error": str(e),
            "result": {"error": str(e)},
            "timestamp": datetime.now().isoformat()
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
        
        # Create specific messages based on the tool type
        if "trend" in tool_name:
            message = f"📈 Analyzing {input_str} trend patterns..."
            details = "Calculating moving averages and trend strength indicators"
        elif "momentum" in tool_name:
            message = f"🚀 Evaluating {input_str} momentum..."
            details = "Computing RSI, MACD, and momentum oscillators"
        elif "mean_reversion" in tool_name:
            message = f"📊 Checking {input_str} mean reversion..."
            details = "Analyzing Bollinger Bands and statistical deviations"
        elif "volatility" in tool_name:
            message = f"📉 Measuring {input_str} volatility..."
            details = "Calculating ATR and volatility regimes"
        elif "support_resistance" in tool_name:
            message = f"🎯 Identifying {input_str} key levels..."
            details = "Finding support and resistance zones"
        else:
            message = f"⚡ Running {tool_name} for {input_str}..."
            details = f"Performing analysis on {input_str}"
            
        self._send_event_sync("tool_start", {
            "tool_name": tool_name,
            "input": input_str,
            "message": message,
            "details": details
        })
    
    def on_tool_end(self, output: str, **kwargs) -> Any:
        """Called when a tool ends."""
        
        # Extract key information from the output to make messages more specific
        message = "📊 Data received"
        details = "Processing results..."
        
        try:
            if "trend" in output and "ADX" in output:
                message = "📈 Trend analysis complete"
                details = "Trend direction and strength determined"
            elif "RSI" in output or "momentum" in output:
                message = "🚀 Momentum indicators calculated"
                details = "Overbought/oversold levels identified"
            elif "z_score" in output or "Bollinger" in output:
                message = "📊 Mean reversion analysis done"
                details = "Statistical extremes evaluated"
            elif "volatility" in output or "ATR" in output:
                message = "📉 Volatility metrics computed"
                details = "Market regime identified"
            elif "support" in output or "resistance" in output:
                message = "🎯 Key levels mapped"
                details = "Support and resistance zones identified"
        except:
            pass  # Use default message if parsing fails
            
        self._send_event_sync("tool_end", {
            "output": output[:200] + "..." if len(output) > 200 else output,
            "message": message,
            "details": details
        })
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> Any:
        """Called when LLM starts thinking."""
        self.current_step += 1
        
        # Vary the thinking messages to be more specific
        thinking_messages = [
            "🤔 Technical Analyst is studying the charts...",
            "🤔 Analyzing price patterns...",
            "🤔 Evaluating technical indicators...",
            "🤔 Identifying trading opportunities...",
            "🤔 Calculating entry and exit points...",
            "🤔 Assessing risk/reward ratios..."
        ]
        
        # Use step to rotate through different messages
        message_index = (self.current_step - 1) % len(thinking_messages)
        
        self._send_event_sync("llm_thinking", {
            "message": thinking_messages[message_index],
            "details": "Processing data with technical analysis methodology",
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

class TechnicalAnalystChatAgent:
    """Technical Analyst specialized chat agent for chart pattern and indicator analysis."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", model_provider: str = "openai"):
        self.model_name = model_name
        self.model_provider = model_provider
        
        # Initialize LLM using existing infrastructure
        self.llm = get_model(model_name, model_provider)
        if self.llm is None:
            raise ValueError(f"Failed to initialize model: {model_name} with provider: {model_provider}")
        
        # Import the existing tools
        from app.backend.services.technical_analyst_chat_agent import (
            technical_trend_analysis,
            technical_momentum_analysis,
            technical_mean_reversion_analysis,
            technical_volatility_analysis,
            technical_support_resistance_analysis
        )
        
        self.tools = [
            technical_trend_analysis,
            technical_momentum_analysis,
            technical_mean_reversion_analysis,
            technical_volatility_analysis,
            technical_support_resistance_analysis
        ]
        
        # Create prompt
        template = """You are a Professional Technical Analyst with expertise in chart patterns, technical indicators, and quantitative trading strategies. You focus on price action, volume, and mathematical indicators to identify trading opportunities without considering fundamental factors.

Your technical analysis approach includes:
- Trend following: Moving averages (SMA, EMA), ADX, trendlines
- Momentum indicators: RSI, MACD, Stochastic, ROC
- Mean reversion: Bollinger Bands, z-scores, standard deviations
- Volatility analysis: ATR, VIX correlation, volatility regimes
- Support and resistance: Pivot points, Fibonacci levels, psychological levels
- Volume analysis: Volume profiles, accumulation/distribution
- Chart patterns: Head and shoulders, triangles, flags, wedges

Trading principles you follow:
- The trend is your friend until it ends
- Let profits run, cut losses short
- Volume confirms price movements
- Multiple timeframe analysis for confirmation
- Risk management is paramount
- Price discounts everything
- History tends to repeat itself
- Markets move in trends

Technical setups you look for:
- Breakouts from consolidation patterns
- Trend continuation patterns
- Reversal patterns at key levels
- Divergences between price and indicators
- Volume climax at tops and bottoms
- Moving average crossovers with volume
- Oversold bounces and overbought pullbacks

You should respond in a technical analyst's style - data-driven, focusing on price action and indicators, using technical jargon appropriately. Reference specific indicator values, chart patterns, and statistical measures. Be objective and avoid emotional language.

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
        Process a natural language financial analysis query with Technical Analyst's perspective.
        
        Args:
            query: Natural language query (e.g., "What do the charts say about Tesla?")
            chat_history: Previous conversation messages
            
        Returns:
            Dict containing analysis results and technical response
        """
        try:
            # Execute the agent
            result = await self.executor.ainvoke({
                "input": query,
                "chat_history": chat_history or []
            })
            
            return {
                "response": result["output"],
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "agent": "technical_analyst"
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error while analyzing your question: {str(e)}",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "agent": "technical_analyst"
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
                "message": "🎯 Starting technical chart analysis...",
                "query": query,
                "agent": "technical_analyst"
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
                # Send contextual heartbeat to keep connection alive
                heartbeat_messages = [
                    "⏳ Analyzing chart patterns...",
                    "⏳ Calculating technical indicators...",
                    "⏳ Identifying support and resistance...",
                    "⏳ Evaluating momentum signals...",
                    "⏳ Checking for divergences...",
                    "⏳ Analyzing volume patterns...",
                    "⏳ Scanning multiple timeframes..."
                ]
                
                import random
                heartbeat = {
                    "type": "heartbeat",
                    "data": {"message": random.choice(heartbeat_messages)},
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
                    "agent": "technical_analyst"
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
                    "agent": "technical_analyst"
                },
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(error_event)

# Global agent instance with lazy initialization
_technical_analyst_agent = None

def get_technical_analyst_agent():
    """Get or create the Technical Analyst chat agent instance."""
    global _technical_analyst_agent
    if _technical_analyst_agent is None:
        _technical_analyst_agent = TechnicalAnalystChatAgent()
    return _technical_analyst_agent

async def process_technical_analyst_query(query: str, chat_history: List = None) -> Dict[str, Any]:
    """
    Process a natural language query using Technical Analysis approach.
    
    Args:
        query: Natural language query about stocks or charts
        chat_history: Previous conversation messages
        
    Returns:
        Dict containing Technical Analyst's analysis and response
    """
    agent = get_technical_analyst_agent()
    return await agent.analyze(query, chat_history) 