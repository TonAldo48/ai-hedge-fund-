"""
Warren Buffett Chat Agent for Natural Language Financial Analysis
"""
import os
from typing import Dict, Any, List, AsyncGenerator, Optional
from datetime import datetime, timedelta
import json
import asyncio

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
        ticker = clean_ticker(ticker)
        end_date = datetime.now().strftime("%Y-%m-%d")
        
        metrics = get_financial_metrics(ticker, end_date, period="annual", limit=5)
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
        if "fundamentals" in tool_name:
            message = f"📊 Analyzing {input_str} fundamentals..."
            details = "Calculating ROE, debt ratios, operating margins, and liquidity metrics"
        elif "moat" in tool_name:
            message = f"🏰 Evaluating {input_str} competitive moat..."
            details = "Checking for durable competitive advantages and pricing power"
        elif "consistency" in tool_name:
            message = f"📈 Examining {input_str} earnings consistency..."
            details = "Analyzing earnings stability and growth patterns over time"
        elif "management" in tool_name:
            message = f"👔 Assessing {input_str} management quality..."
            details = "Evaluating capital allocation, dividends, and shareholder policies"
        elif "intrinsic_value" in tool_name:
            message = f"💰 Calculating {input_str} intrinsic value..."
            details = "Running DCF model with owner earnings and margin of safety"
        elif "owner_earnings" in tool_name:
            message = f"💵 Computing {input_str} owner earnings..."
            details = "Calculating true cash-generating ability of the business"
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
            if "ROE" in output and "debt" in output:
                message = "📊 Fundamentals data collected"
                details = "Found ROE, debt ratios, margins, and liquidity metrics"
            elif "moat" in output or "score" in output:
                message = "🏰 Moat analysis complete"
                details = "Competitive advantage assessment finished"
            elif "earnings" in output and "growth" in output:
                message = "📈 Earnings patterns analyzed"
                details = "Growth consistency evaluation complete"
            elif "dilution" in output or "dividends" in output:
                message = "👔 Management evaluation done"
                details = "Capital allocation assessment complete"
            elif "intrinsic_value" in output or "margin_of_safety" in output:
                message = "💰 Valuation model complete"
                details = "DCF calculation and margin of safety determined"
            elif "owner_earnings" in output:
                message = "💵 Owner earnings calculated"
                details = "True cash-generating ability assessed"
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
            "🤔 Warren Buffett is evaluating the analysis...",
            "🤔 Considering investment implications...",
            "🤔 Weighing the risk-reward balance...",
            "🤔 Applying value investing principles...",
            "🤔 Synthesizing financial data...",
            "🤔 Determining next analysis step..."
        ]
        
        # Use step to rotate through different messages
        message_index = (self.current_step - 1) % len(thinking_messages)
        
        self._send_event_sync("llm_thinking", {
            "message": thinking_messages[message_index],
            "details": "Processing data with Buffett's investment criteria",
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
    
    def __init__(self, model_name: str = "gpt-4o-mini", model_provider: str = "openai"):
        self.model_name = model_name
        self.model_provider = model_provider
        
        # Initialize LLM using existing infrastructure
        self.llm = get_model(model_name, model_provider)
        if self.llm is None:
            raise ValueError(f"Failed to initialize model: {model_name} with provider: {model_provider}")
        
        # Import the existing tools
        from app.backend.services.warren_buffett_chat_agent import (
            warren_buffett_fundamentals_analysis,
            warren_buffett_moat_analysis,
            warren_buffett_consistency_analysis,
            warren_buffett_management_analysis,
            warren_buffett_intrinsic_value_analysis
        )
        
        self.tools = [
            warren_buffett_fundamentals_analysis,
            warren_buffett_moat_analysis,
            warren_buffett_consistency_analysis,
            warren_buffett_management_analysis,
            warren_buffett_intrinsic_value_analysis
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
                "agent": "warren_buffett"
            }
            
        except Exception as e:
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
                # Send contextual heartbeat to keep connection alive
                heartbeat_messages = [
                    "⏳ Retrieving financial data from market sources...",
                    "⏳ Cross-referencing industry benchmarks...",
                    "⏳ Applying Buffett's investment criteria...",
                    "⏳ Calculating complex financial metrics...",
                    "⏳ Evaluating long-term business prospects...",
                    "⏳ Assessing management track record...",
                    "⏳ Comparing to similar investments..."
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

    async def analyze_streaming_v2(self, query: str, chat_history: List = None) -> AsyncGenerator[str, None]:
        """
        Stream the final response from the Warren Buffett agent token by token.
        This is compatible with the Vercel AI SDK's useChat hook.
        """
        # Get the full response from the existing `analyze` method
        # We can reuse the logic without duplicating it
        result = await self.analyze(query, chat_history)
        
        # Simulate a streaming effect for the final response text
        # In a real scenario, you would use the streaming capabilities of the LLM
        response_text = result.get("response", "No response generated.")
        
        # Get the underlying LLM with streaming enabled
        streaming_llm = get_model(
            self.model_name,
            self.model_provider,
            streaming=True
        )

        # Create a simple prompt to generate the final response in a streaming way
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=f"Based on the following analysis, provide a comprehensive answer as Warren Buffett:\n\n{response_text}")
        ]

        # Stream the response from the LLM
        async for chunk in streaming_llm.astream(messages):
            yield chunk.content

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