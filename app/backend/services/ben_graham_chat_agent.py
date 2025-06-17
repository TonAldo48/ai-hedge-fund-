"""
Ben Graham Chat Agent for Natural Language Financial Analysis
"""
import os
from typing import Dict, Any, List, AsyncGenerator, Optional
from datetime import datetime, timedelta
import json
import asyncio
import math

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

# Import Ben Graham analysis functions
from src.agents.ben_graham import (
    analyze_earnings_stability,
    analyze_financial_strength,
    analyze_valuation_graham
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
def ben_graham_earnings_stability_analysis(ticker: str) -> Dict[str, Any]:
    """
    Analyze earnings stability using Benjamin Graham's criteria.
    Graham insisted on at least 5 years of consistently positive earnings.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing earnings stability analysis and consistency assessment
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=10)
        financial_line_items = search_line_items(
            ticker,
            ["earnings_per_share", "revenue", "net_income"],
            end_date,
            period="annual",
            limit=10
        )
        
        result = analyze_earnings_stability(metrics, financial_line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "ben_graham_earnings_stability",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "ben_graham_earnings_stability",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def ben_graham_financial_strength_analysis(ticker: str) -> Dict[str, Any]:
    """
    Evaluate financial strength using Graham's conservative criteria.
    Focuses on current ratio (>=2), low debt, and dividend consistency.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing financial strength metrics and safety assessment
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            [
                "total_assets", "total_liabilities", "current_assets", 
                "current_liabilities", "dividends_and_other_cash_distributions", 
                "shareholders_equity"
            ],
            end_date,
            period="annual",
            limit=10
        )
        
        result = analyze_financial_strength(financial_line_items)
        
        return {
            "ticker": ticker,
            "analysis_type": "ben_graham_financial_strength",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "ben_graham_financial_strength",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def ben_graham_margin_of_safety_analysis(ticker: str) -> Dict[str, Any]:
    """
    Calculate margin of safety using Graham's valuation methods.
    Includes Net-Net analysis and Graham Number calculation.
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing valuation analysis with margin of safety calculation
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            [
                "current_assets", "total_liabilities", "book_value_per_share",
                "earnings_per_share", "outstanding_shares", "total_assets"
            ],
            end_date,
            period="annual",
            limit=5
        )
        
        market_cap = get_market_cap(ticker, end_date)
        result = analyze_valuation_graham(financial_line_items, market_cap)
        
        return {
            "ticker": ticker,
            "analysis_type": "ben_graham_margin_of_safety",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "ben_graham_margin_of_safety",
            "error": str(e),
            "result": {"score": 0, "details": f"Error: {str(e)}"},
            "timestamp": datetime.now().isoformat()
        }

@tool
def ben_graham_intrinsic_value_analysis(ticker: str) -> Dict[str, Any]:
    """
    Calculate intrinsic value using Graham's formula.
    Graham Number = sqrt(22.5 × EPS × Book Value per Share)
    
    Args:
        ticker: Stock ticker symbol (e.g., TSLA, AAPL)
    
    Returns:
        Dict containing intrinsic value calculation and investment recommendation
    """
    try:
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        financial_line_items = search_line_items(
            ticker,
            ["earnings_per_share", "book_value_per_share", "outstanding_shares"],
            end_date,
            period="annual",
            limit=1
        )
        
        market_cap = get_market_cap(ticker, end_date)
        
        if not financial_line_items:
            raise ValueError("No financial data available")
        
        latest = financial_line_items[0]
        eps = latest.earnings_per_share or 0
        bvps = latest.book_value_per_share or 0
        shares = latest.outstanding_shares or 0
        
        graham_number = None
        margin_of_safety = None
        
        if eps > 0 and bvps > 0:
            graham_number = math.sqrt(22.5 * eps * bvps)
            
            if market_cap and shares > 0:
                current_price = market_cap / shares
                margin_of_safety = (graham_number - current_price) / current_price
        
        result = {
            "graham_number": graham_number,
            "current_price": market_cap / shares if market_cap and shares > 0 else None,
            "margin_of_safety": margin_of_safety,
            "eps": eps,
            "book_value_per_share": bvps,
            "recommendation": "Buy" if margin_of_safety and margin_of_safety > 0.3 else 
                            "Hold" if margin_of_safety and margin_of_safety > 0 else "Avoid"
        }
        
        return {
            "ticker": ticker,
            "analysis_type": "ben_graham_intrinsic_value",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "ticker": clean_ticker(ticker) if ticker else "UNKNOWN",
            "analysis_type": "ben_graham_intrinsic_value",
            "error": str(e),
            "result": {"graham_number": None, "error": f"Error: {str(e)}"},
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
        if "earnings_stability" in tool_name:
            message = f"📊 Analyzing {input_str} earnings stability..."
            details = "Checking for consistent positive earnings over multiple years"
        elif "financial_strength" in tool_name:
            message = f"💪 Evaluating {input_str} financial strength..."
            details = "Assessing liquidity, debt levels, and dividend history"
        elif "margin_of_safety" in tool_name:
            message = f"🔍 Calculating {input_str} margin of safety..."
            details = "Performing Net-Net and Graham Number valuation"
        elif "intrinsic_value" in tool_name:
            message = f"💰 Computing {input_str} intrinsic value..."
            details = "Applying Graham's valuation formula"
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
            if "earnings" in output and "stability" in output:
                message = "📊 Earnings analysis complete"
                details = "Earnings consistency evaluated"
            elif "current ratio" in output or "debt" in output:
                message = "💪 Financial strength assessed"
                details = "Balance sheet metrics analyzed"
            elif "Graham Number" in output or "margin of safety" in output:
                message = "🔍 Valuation calculated"
                details = "Margin of safety determined"
            elif "intrinsic" in output:
                message = "💰 Intrinsic value computed"
                details = "Graham formula applied"
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
            "🤔 Ben Graham is evaluating the fundamentals...",
            "🤔 Calculating margin of safety...",
            "🤔 Assessing financial conservatism...",
            "🤔 Applying value investing principles...",
            "🤔 Checking defensive criteria...",
            "🤔 Determining investment merit..."
        ]
        
        # Use step to rotate through different messages
        message_index = (self.current_step - 1) % len(thinking_messages)
        
        self._send_event_sync("llm_thinking", {
            "message": thinking_messages[message_index],
            "details": "Processing data with Graham's value investing criteria",
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

class BenGrahamChatAgent:
    """Ben Graham specialized chat agent for deep value investing analysis."""
    
    def __init__(self, model_name: str = "gpt-4o-mini", model_provider: str = "openai"):
        self.model_name = model_name
        self.model_provider = model_provider
        
        # Initialize LLM using existing infrastructure
        self.llm = get_model(model_name, model_provider)
        if self.llm is None:
            raise ValueError(f"Failed to initialize model: {model_name} with provider: {model_provider}")
        
        # Import the existing tools
        from app.backend.services.ben_graham_chat_agent import (
            ben_graham_earnings_stability_analysis,
            ben_graham_financial_strength_analysis,
            ben_graham_margin_of_safety_analysis,
            ben_graham_intrinsic_value_analysis
        )
        
        self.tools = [
            ben_graham_earnings_stability_analysis,
            ben_graham_financial_strength_analysis,
            ben_graham_margin_of_safety_analysis,
            ben_graham_intrinsic_value_analysis
        ]
        
        # Create prompt
        template = """You are Benjamin Graham, the father of value investing and author of "The Intelligent Investor" and "Security Analysis". You taught Warren Buffett at Columbia Business School and are known for your systematic, analytical approach to investing based on fundamental analysis and the concept of margin of safety.

Your investment philosophy includes:
- Margin of safety is the central concept of investment
- Distinguish between investment and speculation
- Focus on intrinsic value, not market price
- Prefer defensive investing over aggressive strategies
- Insist on financial strength and earnings stability
- The market is there to serve you, not to instruct you (Mr. Market analogy)
- Price is what you pay, value is what you get
- In the short run, the market is a voting machine; in the long run, it's a weighing machine

Your analytical criteria include:
- Adequate size of the enterprise
- Strong financial condition (current ratio > 2)
- Earnings stability (positive earnings for at least 10 years)
- Dividend record (uninterrupted payments for 20 years)
- Earnings growth (at least one-third over 10 years)
- Moderate P/E ratio (< 15x average earnings)
- Moderate price to book ratio (< 1.5x)

Special situations you look for:
- Net-Net stocks (market cap < net current asset value)
- Graham Number opportunities (price < sqrt(22.5 × EPS × BVPS))
- Bargain issues selling below liquidation value

You should respond in Benjamin Graham's characteristic style - academic, methodical, conservative, emphasizing quantitative analysis and downside protection. Reference your books and academic work when relevant.

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
        Process a natural language financial analysis query with Ben Graham's perspective.
        
        Args:
            query: Natural language query (e.g., "What's the margin of safety for Apple?")
            chat_history: Previous conversation messages
            
        Returns:
            Dict containing analysis results and Graham-style response
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
                "agent": "ben_graham"
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error while analyzing your question: {str(e)}",
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat(),
                "agent": "ben_graham"
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
                "message": "🎯 Starting Benjamin Graham value analysis...",
                "query": query,
                "agent": "ben_graham"
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
                    "⏳ Analyzing earnings stability...",
                    "⏳ Evaluating financial strength...",
                    "⏳ Calculating margin of safety...",
                    "⏳ Checking Graham criteria...",
                    "⏳ Computing intrinsic value...",
                    "⏳ Assessing defensive characteristics...",
                    "⏳ Applying value investing principles..."
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
                    "agent": "ben_graham"
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
                    "agent": "ben_graham"
                },
                "timestamp": datetime.now().isoformat()
            }
            yield json.dumps(error_event)

# Global agent instance with lazy initialization
_ben_graham_agent = None

def get_ben_graham_agent():
    """Get or create the Ben Graham chat agent instance."""
    global _ben_graham_agent
    if _ben_graham_agent is None:
        _ben_graham_agent = BenGrahamChatAgent()
    return _ben_graham_agent

async def process_ben_graham_query(query: str, chat_history: List = None) -> Dict[str, Any]:
    """
    Process a natural language query using Ben Graham's value investing approach.
    
    Args:
        query: Natural language query about stocks or investing
        chat_history: Previous conversation messages
        
    Returns:
        Dict containing Ben Graham's analysis and response
    """
    agent = get_ben_graham_agent()
    return await agent.analyze(query, chat_history) 